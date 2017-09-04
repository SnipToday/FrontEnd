from django.test import TestCase
# Create your tests here.
from django.urls import reverse
from snips.models import Snip, SnipRelatedLink, Category, SnipLog, Vote, PostMetrics
from django.contrib import auth
from . import test_utils as tu
import pytest


@pytest.fixture(autouse=True)
def setup_categories():
    tu.create_categories()


def test_user_logged(client):
    """ Test user logged in """
    u = tu.create_user(username='test1')
    client.login(email=u.email, password=tu.DEF_PASS)
    client_user = auth.get_user(client)
    assert client_user == u
    assert client_user.is_authenticated()


def test_vote_errors(client):
    """ Test illegal posts of votes are being recognized """
    s = tu.create_snip('test1', category=Category.objects.all()[0], is_locked=Snip.FREE)
    url = reverse('snips:log', args=[s.id])
    res = client.post(url, {'action': SnipLog.LIKE, 'param1': Vote.MARK_VOTE})
    assert tu.res_to_json(res) == {'message': 'signin'}

    res = client.post(url, {'param1': Vote.MARK_VOTE})
    assert tu.res_to_json(res) == {'message': 'Failed to get action'}

    u = tu.create_user(username='test1')
    client.login(email=u.email, password=tu.DEF_PASS)
    res = client.post(url, {'action': SnipLog.LIKE})
    assert tu.res_to_json(res) == {'message': 'missing vote action'}


def prepare_users_and_snip(client):
    u = tu.create_user(username='test1')
    u2 = tu.create_user(username='test2', email='jon2@snip.today')
    client.login(email=u.email, password=tu.DEF_PASS)
    s = tu.create_snip('test1', category=Category.objects.all()[0], is_locked=Snip.FREE)
    url = reverse('snips:log', args=[s.id])
    return u, u2, s, url


@pytest.mark.parametrize('action', [SnipLog.SHARE, SnipLog.VIEWED, SnipLog.READ_MORE, SnipLog.OPEN_LINK])
def test_post_metric(client, action):
    """ Test posting user action increase PostMetric unless action already been posted by the user """
    u, u2, s, url = prepare_users_and_snip(client)
    client.post(url, {'action': action})
    assert getattr(PostMetrics.objects.get(snip=s), action) == 1
    client.post(url, {'action': action})
    assert getattr(PostMetrics.objects.get(snip=s), action) == 1

    client.login(email=u2.email, password=tu.DEF_PASS)
    client.post(url, {'action': action})
    assert getattr(PostMetrics.objects.get(snip=s), action), 2


@pytest.mark.parametrize('action', [SnipLog.LIKE, SnipLog.DISLIKE])
def test_vote_metric(client, action):
    """ Test posting and undoing votes increase and decrease PostMetric unless action already been posted by the user"""
    u, u2, s, url = prepare_users_and_snip(client)
    client.post(url, {'action': action, 'param1': Vote.MARK_VOTE})
    assert getattr(PostMetrics.objects.get(snip=s), action) == 1
    client.post(url, {'action': action, 'param1': Vote.MARK_VOTE})
    assert getattr(PostMetrics.objects.get(snip=s), action) == 1

    client.login(email=u2.email, password=tu.DEF_PASS)
    client.post(url, {'action': action, 'param1': Vote.MARK_VOTE})
    assert getattr(PostMetrics.objects.get(snip=s), action) == 2

    client.post(url, {'action': action, 'param1': Vote.REMOVE_VOTE})
    assert getattr(PostMetrics.objects.get(snip=s), action) == 1

    client.login(email=u2.email, password=tu.DEF_PASS)
    client.post(url, {'action': action, 'param1': Vote.REMOVE_VOTE})
    assert getattr(PostMetrics.objects.get(snip=s), action) == 0


@pytest.mark.parametrize('action', [SnipLog.LIKE, SnipLog.DISLIKE])
def test_vote_model(client, action):
    """ Test posting votes by user are creating and removing Vote object """
    u, u2, s, url = prepare_users_and_snip(client)
    client.post(url, {'action': action, 'param1': Vote.MARK_VOTE})
    assert Vote.objects.filter(snip=s, user=u, vote=action).exists()
    client.post(url, {'action': action, 'param1': Vote.MARK_VOTE})
    assert Vote.objects.filter(snip=s, user=u, vote=action).count() == 1

    client.login(email=u2.email, password=tu.DEF_PASS)
    client.post(url, {'action': action, 'param1': Vote.MARK_VOTE})
    assert Vote.objects.filter(snip=s, vote=action).count() == 2

    client.login(email=u.email, password=tu.DEF_PASS)
    client.post(url, {'action': action, 'param1': Vote.REMOVE_VOTE})
    assert not Vote.objects.filter(snip=s, user=u, vote=action).exists()