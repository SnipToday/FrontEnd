import os

import logging

import facebook
import tweepy
from django.contrib.sites.models import Site
from django.template.defaultfilters import striptags
from django.urls import reverse
from huey import crontab
from huey.contrib.djhuey import db_periodic_task, db_task
from django.core import management
from tweepy import TweepError

logger = logging.getLogger(__name__)

@db_periodic_task(crontab(minute='*/5', hour='*'))
def run_wagtail_publish_command():
    management.call_command('publish_scheduled_pages')


def get_full_url(post):
    rel_url = reverse('snips:post', args=[post.slug])
    domain = Site.objects.get_current().domain
    url = 'https://' + domain + rel_url
    return url


def shorten_text(text, max_len):
    text = striptags(text)
    text = text[:max_len]
    text = text[:text.rfind(' ')]
    text += '...'
    return text


@db_task()
def publish_on_twitter(post):
    TWTR_MAX_CHARS_WITH_URL = 115
    if not post.post_on_twtr:
        logger.info('Posting to TWTR not requested - %s' % post.slug)
        return
    if post.twtr_post_id:
        logger.info('Already posted on TWTR - %s' % post.slug)
        return

    logger.info('Posting on TWTR - %s' % post.slug)
    url = get_full_url(post)
    try:
        api = get_twitter_api()
    except Exception as e:
        logger.exception('Failed to create TWTR api object - %s' % e)
        return
    try:
        title = post.title
        if len(title) > TWTR_MAX_CHARS_WITH_URL:
            title = shorten_text(title, TWTR_MAX_CHARS_WITH_URL-3)
        res = api.update_status(title + ' ' + url)
        post.twtr_post_id = res.id_str
        post.save()
        logger.info('Post in now on TWTR - %s' % post.slug)
    except TweepError as e:
        logger.exception('Failed to post on twtr - %s - %s' % (post.slug, e))


def get_fb_page_api():
    graph = facebook.GraphAPI(access_token=os.environ.get('FB_TOKEN'), version='2.7')
    page_access = graph.get_object(os.environ.get('FB_PAGE'), **{'fields': 'access_token'})['access_token']
    return facebook.GraphAPI(access_token=page_access, version='2.7')


@db_task()
def publish_on_facebook(post):
    if not post.post_on_fb:
        logger.info('Posting to FB not requested - %s' % post.slug)
        return
    if post.fb_post_id:
        logger.info('Already posted on FB - %s' % post.slug)
        return
    MAX_BODY_LEN = 150
    body = shorten_text(post.body, MAX_BODY_LEN)
    logger.info('Posting on FB - %s' % post.slug)
    url = get_full_url(post)
    try:
        graph = get_fb_page_api()
        attachment = {'link': url, 'description': body, 'name': post.title}
        res = graph.put_wall_post(message='', attachment=attachment, profile_id=os.environ.get('FB_PAGE'))
        post.fb_post_id = res['id']
        post.save()
        logger.info('Post is in now on FB - %s' % post.slug)
    except Exception as e:
        logger.exception('Failed to post on FB - %s - %s' % (post.slug, e))


def get_twitter_api(wait_on_rate_limit=True):
    consumer_key = os.environ.get('TWTR_CONSUMER_KEY')
    consumer_secret = os.environ.get('TWTR_CONSUMER_SECRET')
    access_token = os.environ.get('TWTR_ACCESS_TOKEN')
    access_secret = os.environ.get('TWTR_ACCESS_SECRET')
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_secret)
    return tweepy.API(auth, wait_on_rate_limit=wait_on_rate_limit, wait_on_rate_limit_notify=True)

