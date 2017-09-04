# Create your tests here.
from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone
from snips.models import Snip, SnipRelatedLink, Category, SnipLog, Vote, PostMetrics
from . import test_utils as tu


@pytest.fixture(autouse=True)
def setup_categories():
    tu.create_categories()


def test_snip_live(client):
    """ Test posts returns only live snips """
    tu.create_snip('test1', category=Category.objects.all()[0], is_locked=Snip.FREE, live=False)
    response = client.get(reverse('snips:posts'))
    assert response.context[0]['posts'] == []

    s = tu.create_snip('test1', category=Category.objects.all()[0], is_locked=Snip.FREE)
    response = client.get(reverse('snips:posts'))
    assert response.context[0]['posts'] == [s]


def get_infinite_all_posts(client, base_url, num_posts):
    posts = []
    page_size = 2
    response = client.get(base_url)
    posts += response.context[0]['posts']
    for i in range(1, int(num_posts / page_size) + 2):
        response = client.get(base_url, {'page': i})
        posts += response.context[0]['posts']
    return posts


def test_infinite_scroll(client):
    """ Test infinite scroll returns all posts """
    num_posts = 20
    for i in range(num_posts):
        tu.create_snip('test_%s' % i, category=Category.objects.all()[0], is_locked=Snip.FREE)
    posts = get_infinite_all_posts(client, reverse('snips:posts'), num_posts)
    ids = [p.id for p in posts]
    assert len(set(ids)) == num_posts


def test_direct_link_to_post(client):
    """ Test direct link to post return him first and only once"""
    for i in range(5):
        tu.create_snip('test_%s' % i, category=Category.objects.all()[0], is_locked=Snip.FREE)
    s = tu.create_snip('test1', category=Category.objects.all()[0], is_locked=Snip.FREE)
    for i in range(5):
        tu.create_snip('test_%s' % i, category=Category.objects.all()[0], is_locked=Snip.LOCKED)
    posts = get_infinite_all_posts(client, reverse('snips:post', args=[s.slug]), 11)
    assert posts[0] == s
    assert s not in posts[1:]


def test_post_metrics_auto_create():
    """ Test PostMetrics object is created automatically after post creation """
    s = tu.create_snip('test1', category=Category.objects.all()[0], is_locked=Snip.FREE)
    assert PostMetrics.objects.filter(snip=s).exists()


def create_posts_with_likes(client, num_posts):
    u = tu.create_user(username='test1')
    client.login(email=u.email, password=tu.DEF_PASS)
    liked_p_id = []
    disliked_p_id = []
    other_p_id = []
    for i in range(num_posts):
        s = tu.create_snip('test_%s' % i, category=Category.objects.all()[0], is_locked=Snip.FREE)
        url = reverse('snips:log', args=[s.id])
        if i % 2 == 0:
            client.post(url, {'action': SnipLog.LIKE, 'param1': Vote.MARK_VOTE})
            liked_p_id.append(s.id)
        elif i % 3 == 0:
            client.post(url, {'action': SnipLog.DISLIKE, 'param1': Vote.MARK_VOTE})
            disliked_p_id.append(s.id)
        else:
            other_p_id.append(s.id)
    return liked_p_id, disliked_p_id, other_p_id


def test_only_liked(client):
    num_posts = 20
    liked_p_id, disliked_p_id, other_p_id = create_posts_with_likes(client, num_posts)
    posts = get_infinite_all_posts(client, reverse('snips:profile'), int(num_posts / 2) + 1)
    assert sorted([p.id for p in posts]) == liked_p_id


def test_categories(client):
    first_cat = Category.objects.all()[0]
    sec_cat = Category.objects.all()[1]
    for i in range(5):
        tu.create_snip('test_%s' % i, category=first_cat)
    sec_cat_posts = []
    for i in range(5):
        sec_cat_posts.append(tu.create_snip('test_%s' % i, category=sec_cat))
    url = reverse('snips:posts') + "?category=%d" % sec_cat.id
    posts = get_infinite_all_posts(client, url, 5)
    assert posts == sec_cat_posts


def test_feed_no_votes(client):
    num_posts = 30
    liked_p_id, disliked_p_id, other_p_id = create_posts_with_likes(client, num_posts)
    posts = get_infinite_all_posts(client, reverse('snips:posts'), int(num_posts / 2) + 1)
    assert sorted([p.id for p in posts]) == other_p_id


def test_locked_free_merging(client):
    num_posts = 20
    u = tu.create_user(username='test1')
    client.login(email=u.email, password=tu.DEF_PASS)
    for i in range(num_posts):
        locked = Snip.FREE
        if i >= num_posts / 2:
            locked = Snip.LOCKED
        tu.create_snip('test_%s' % i, category=Category.objects.all()[0], is_locked=locked)
    posts = get_infinite_all_posts(client, reverse('snips:posts'), int(num_posts / 2) + 1)
    for j, p in enumerate(posts):
        locked = (Snip.FREE if j % 2 == 0 else Snip.LOCKED)
        assert p.is_locked == locked


def test_ignore_locked_for_subsbscribe(client):
    num_posts = 6
    orig_posts = []
    u = tu.create_user(username='test1', is_subscribed=True)
    client.login(email=u.email, password=tu.DEF_PASS)
    publish_date = timezone.now()
    for i in range(num_posts):
        is_lock = Snip.FREE if i % 2 == 0 else Snip.LOCKED
        s = tu.create_snip('test_%s' % i, category=Category.objects.all()[0], is_locked=is_lock, publish_date=publish_date)
        s.postmetrics.like = i + (i % 2) * 10
        s.postmetrics.dislike = num_posts - i
        s.postmetrics.save()
        orig_posts.append(s)

    posts = get_infinite_all_posts(client, reverse('snips:posts'), int(num_posts / 2) + 1)
    assert posts == [orig_posts[5], orig_posts[3], orig_posts[1], orig_posts[4], orig_posts[2], orig_posts[0]]


def test_popularity_effect(client):
    """ Test post popularity ordering """
    num_posts = 10
    orig_posts = []
    u = tu.create_user(username='test1')
    client.login(email=u.email, password=tu.DEF_PASS)
    publish_date = timezone.now()
    death_days = 3
    for i in range(num_posts):
        s = tu.create_snip('test_%s' % i, category=Category.objects.all()[0], is_locked=Snip.FREE,
                           death_days=death_days, publish_date=publish_date)
        s.postmetrics.like = i
        s.postmetrics.dislike = num_posts - i
        s.postmetrics.save()
        orig_posts.append(s)

    posts = get_infinite_all_posts(client, reverse('snips:posts'), int(num_posts / 2) + 1)
    assert posts == orig_posts[::-1]


def test_death_date_effect_shortly_after_publish(client):
    """ Test post death date effect """
    num_posts = 5
    orig_posts = []
    u = tu.create_user(username='test1')
    client.login(email=u.email, password=tu.DEF_PASS)
    publish_date = timezone.now()
    for i in range(num_posts):
        s = tu.create_snip('test_%s' % i, category=Category.objects.all()[0], is_locked=Snip.FREE,
                           death_days=4*i+1, publish_date=publish_date - timedelta(days=0.2))
        s.postmetrics.like = 10
        s.postmetrics.save()
        orig_posts.append(s)

    posts = get_infinite_all_posts(client, reverse('snips:posts'), int(num_posts / 2) + 1)
    assert posts == orig_posts


def test_death_date_effect_long_after_publish(client):
    """ Test post death date effect """
    num_posts = 3
    orig_posts = []
    u = tu.create_user(username='test1')
    client.login(email=u.email, password=tu.DEF_PASS)
    publish_date = timezone.now()
    for i in range(num_posts):
        s = tu.create_snip('test_%s' % i, category=Category.objects.all()[0], is_locked=Snip.FREE,
                           death_days=4*i+1, publish_date=publish_date - timedelta(days=5))
        s.postmetrics.like = 10
        s.postmetrics.save()
        orig_posts.append(s)

    posts = get_infinite_all_posts(client, reverse('snips:posts'), int(num_posts / 2) + 1)
    assert posts == orig_posts[::-1]


def test_user_attitude_effect(client):
    """ Test post death date effect """
    num_posts = 16
    orig_posts = []
    u = tu.create_user(username='test1')
    client.login(email=u.email, password=tu.DEF_PASS)
    publish_date = timezone.now()
    categories = Category.objects.all()
    for i in range(num_posts):
        s = tu.create_snip('test_%s' % i, category=categories[i % 2],
                           is_locked=Snip.FREE, publish_date=publish_date)
        s.postmetrics.like = 10
        s.postmetrics.save()
        orig_posts.append(s)

    for i in range(6):
        Vote.objects.create(snip=orig_posts[i], user=u, vote=SnipLog.LIKE)
    for i in range(6, 10):
        Vote.objects.create(snip=orig_posts[i], user=u, vote=SnipLog.DISLIKE)
    Vote.objects.create(snip=orig_posts[10], user=u, vote=SnipLog.DISLIKE)
    posts = get_infinite_all_posts(client, reverse('snips:posts'), int(num_posts / 2) + 1)
    ordered_posts = [orig_posts[11], orig_posts[13], orig_posts[15], orig_posts[12], orig_posts[14]]
    assert posts == ordered_posts

    # check case where not enough votes
    s = tu.create_snip('test_extra', category=categories[2],
                       is_locked=Snip.FREE, publish_date=publish_date)
    s.postmetrics.like = 10
    s.postmetrics.save()
    posts = get_infinite_all_posts(client, reverse('snips:posts'), int(num_posts / 2) + 1)
    ordered_posts = [orig_posts[11], orig_posts[13], orig_posts[15], s, orig_posts[12], orig_posts[14]]
    assert posts == ordered_posts