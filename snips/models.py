from __future__ import unicode_literals

import json
import os

from dal_select2.widgets import ModelSelect2
from django.contrib.sitemaps import ping_google
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from model_utils import Choices
import copy
from datetime import timedelta

from model_utils.fields import MonitorField
from simple_history.models import HistoricalRecords
from timezone_field import TimeZoneField

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from wagtail.wagtailadmin.forms import WagtailAdminPageForm
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailcore.models import Page, Orderable
from wagtail.wagtailadmin.edit_handlers import (FieldPanel, PageChooserPanel, InlinePanel,
                                                MultiFieldPanel, TabbedInterface, ObjectList)
from wagtail.wagtailcore.signals import page_published
from . import tasks
from modelcluster.fields import ParentalKey
from wagtail.wagtaildocs.edit_handlers import DocumentChooserPanel
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtailsearch import index
import random
import string


class LinkFields(models.Model):
    link_external = models.URLField("External link", max_length=800, blank=True)
    link_page = models.ForeignKey('wagtailcore.Page', null=True, blank=True, related_name='+')

    @property
    def link(self):
        if self.link_page:
            return self.link_page.url
        else:
            return self.link_external

    panels = [
        FieldPanel('link_external'),
        PageChooserPanel('link_page'),
    ]

    class Meta:
        abstract = True


# Related links
class RelatedLink(LinkFields):
    title = models.CharField(max_length=255)
    panels = [
        FieldPanel('title'),
        MultiFieldPanel(LinkFields.panels, "Link"),
    ]

    class Meta:
        abstract = True

    def __unicode__(self):
        return '%s: %s' % (self.title, self.link)


def generate_random_id():
    return ''.join([random.choice(string.digits) for n in range(32)])


class SnipPageForm(WagtailAdminPageForm):

    def save(self, commit=True):
        page = super(SnipPageForm, self).save(commit=False)
        if page.publish_at:
            publish_t = copy.deepcopy(page.publish_at)
            time_diff = page.tzone.localize(publish_t.replace(tzinfo=None)).utcoffset().total_seconds()
            page.go_live_at = page.publish_at - timedelta(seconds=time_diff)
        else:
            page.go_live_at = None
        if commit:
            page.save()
        return page


class Snip(Page):
    base_form_class = SnipPageForm

    date = models.DateField("Post date", default=timezone.now, blank=True)
    body = RichTextField('Body')
    author = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    image1 = models.ForeignKey('images.SnipImage', on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    image2 = models.ForeignKey('images.SnipImage', on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    video = models.ForeignKey('wagtaildocs.Document', null=True, blank=True, on_delete=models.SET_NULL, related_name='+')

    category = models.ForeignKey("Category", on_delete=models.SET_NULL, null=True)

    LOCKED = 'LO'
    FREE = 'FR'
    NOT_DECIDE = 'ND'

    LOCK_CHOICES = ((LOCKED, 'Locked'), (FREE, 'Free'),)

    is_locked = models.CharField('Locked', max_length=2, choices=LOCK_CHOICES)

    show_in_main = models.BooleanField('Show in Main Feed', default=True)

    comments_id = models.CharField(max_length=32, default=generate_random_id)

    publish_at = models.DateTimeField(
        verbose_name="Publish date/time",
        help_text="Please add a date-time in the form YYYY-MM-DD hh:mm.",
        blank=True,
        null=True
    )
    tzone = TimeZoneField(verbose_name='Publish Timezone', default='America/New_York')

    death_days = models.IntegerField('Days to live')
    death_factor = models.FloatField("Alpha value for death decay function", default=0.85)  # 0.85 = decay to 20% in 7 days

    post_on_twtr = models.BooleanField('Post on Twitter', default=False)
    twtr_post_id = models.CharField('Twitter ID', max_length=50, null=True, blank=True)

    post_on_fb = models.BooleanField('Post on Facebook', default=False)
    fb_post_id = models.CharField('Facebook ID', max_length=50, null=True, blank=True)

    search_fields = Page.search_fields + [  # Inherit search_fields from Page
        index.SearchField('body'),
        index.FilterField('date'),
    ]

    content_panels = Page.content_panels + [
        FieldPanel('body'),
        FieldPanel('is_locked'),
        MultiFieldPanel([ImageChooserPanel('image1'),ImageChooserPanel('image2'),DocumentChooserPanel('video')],
                        heading='Media', classname="collapsible"),
        FieldPanel('category'),
        FieldPanel('author', widget=ModelSelect2(url='snips:user-autocomplete')),
        FieldPanel('show_in_main'),
        MultiFieldPanel([FieldPanel('post_on_twtr'), FieldPanel('post_on_fb'),
                         FieldPanel('twtr_post_id'), FieldPanel('fb_post_id')], #  widget=TextInput(attrs={'readonly':'readonly'})
                        heading='Social Media', classname="collapsible"),
        MultiFieldPanel([FieldPanel('publish_at'), FieldPanel('tzone'), FieldPanel('death_days')],
                        heading='Scheduling and death', classname="collapsible"),
        MultiFieldPanel([InlinePanel('related_links', min_num=0)],
                        heading='Related links', classname="collapsible"),
    ]

    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading='Content'),
        ObjectList(Page.promote_panels, heading='Promote'),
    ])

    def clean(self):
        with open(os.environ.get('DECAY_DICT_FILE'), 'r') as infile:
            death_factor_dict = json.loads(infile.read())
        try:
            self.death_factor = float(death_factor_dict[str(self.death_days)])
        except KeyError as e:
            raise ValidationError({'death_days': 'Illegal value, probably too high'})

    def get_absolute_url(self):
        return reverse('snips:post', kwargs={'slug': self.slug})


class SnipRelatedLink(Orderable, RelatedLink):
    page = ParentalKey('Snip', related_name='related_links')


class Category(models.Model):
    name = models.CharField(max_length=60)
    display_name = models.CharField(max_length=60)

    def __str__(self):
        return '%s' % self.display_name

class AbstractOwner(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, db_index=True)
    session = models.CharField(max_length=32, null=True, blank=True, db_index=True)

    class Meta:
        abstract = True


class SnipLog(AbstractOwner):
    READ_MORE = 'readmore'
    LOCKED = 'locked'
    SHARE = 'share'
    VIEWED = 'viewed'
    LIKE = 'like'
    DISLIKE = 'dislike'
    OPEN_LINK = 'open_link'
    LIKE_NOAUTH = 'like_noauth'
    DISLIKE_NOAUTH = 'dislike_noauth'
    REACH_LIMIT = 'reach_limit'
    LOG_ACTIONS = Choices(READ_MORE, LIKE, DISLIKE, SHARE, VIEWED, LOCKED, OPEN_LINK,
                          REACH_LIMIT, LIKE_NOAUTH, DISLIKE_NOAUTH)

    snip = models.ForeignKey(Snip, null=True, blank=True)
    action = models.CharField(max_length=20, choices=LOG_ACTIONS, verbose_name='action')
    param1 = models.CharField(max_length=20, null=True, blank=True)
    param2 = models.CharField(max_length=20, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True, verbose_name='date')
    history = HistoricalRecords()

    class Meta:
        ordering = ['-date']


class Vote(models.Model):
    MARK_VOTE = 'mark_vote'
    REMOVE_VOTE = 'remove_vote'
    VOTE_CHOICES = Choices(SnipLog.LIKE, SnipLog.DISLIKE)

    snip = models.ForeignKey(Snip)
    user = models.ForeignKey(User)
    vote = models.CharField(max_length=10, choices=VOTE_CHOICES)
    date = MonitorField(monitor='vote')

    class Meta:
        unique_together = ("snip", "user")


class PostMetrics(models.Model):
    snip = models.OneToOneField(Snip)
    like = models.IntegerField(default=0)
    dislike = models.IntegerField(default=0)
    share = models.IntegerField(default=0)
    viewed = models.IntegerField(default=0)
    readmore = models.IntegerField(default=0)
    open_link = models.IntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.date = timezone.now()
        super(PostMetrics, self).save(*args, **kwargs)


class Message(models.Model):
    text = models.TextField()
    live = models.BooleanField(default=True)


@receiver(post_save, sender=Snip)
def create_post_metrics(sender, instance, created, **kwargs):
    if created:
        PostMetrics.objects.create(snip=instance)


class Referer(AbstractOwner):
    MAX_URL_LENGTH = 500
    date = models.DateTimeField(auto_now_add=True)
    referer = models.CharField(max_length=MAX_URL_LENGTH)


@receiver(page_published, sender=Snip)
def on_post_live(sender, instance, **kwargs):
    tasks.publish_on_twitter(instance)
    tasks.publish_on_facebook(instance)
    try:
        from django.conf import settings
        if not settings.DEBUG:
            ping_google()
    except Exception as e:
        pass