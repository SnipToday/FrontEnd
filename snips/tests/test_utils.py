import json
from datetime import timedelta
from django.contrib.auth.models import User
from django.utils import timezone
from images.models import SnipImage
from snips.models import Snip, SnipRelatedLink, Category, SnipLog, Vote, PostMetrics
from wagtail.wagtailcore.models import Page
from wagtail.wagtailimages.tests.utils import get_test_image_file

DEF_PASS = 'pass1234'


def create_link(post, title='link_title', link='https://snip.today/'):
    return SnipRelatedLink(page=post, title=title, author='', link_external=link)


def create_image():
    return SnipImage.objects.create(title='Test image', file=get_test_image_file())


def create_user(username, email='a@snip.com', is_subscribed=False):
    u = User.objects.create_user(username=username, email=email, password=DEF_PASS)
    u.profile.subscribed = is_subscribed
    u.profile.save()
    return u

CATEGORY_BASE = 'cat_'


def create_categories():
    for i in range(10):
        Category.objects.create(name=CATEGORY_BASE + str(i))


def create_snip(title, category, image=None, is_locked=Snip.FREE, publish_date=timezone.now(), death_days=3, live=True):
    s = Snip(title=title, body='Short text', live=live, category=category,
             is_locked=is_locked, death_days=death_days)
    if not image:
        s.image = create_image()
    s.date = s.first_published_at = publish_date
    Page.objects.all()[0].add_child(instance=s)
    s.save()
    return s


def res_to_json(res):
    return json.loads(str(res.content, encoding='utf8'))