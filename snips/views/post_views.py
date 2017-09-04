import json
from itertools import chain

import logging

from django.contrib import messages
from django.contrib.messages import get_messages
from django.forms import ModelForm
from django.http import Http404
from django.shortcuts import redirect, render
from django.views.generic import ListView
from userProfile.models import Profile

from ..tasks import shorten_text
from ..models import Snip, Category, Vote, SnipLog, Referer, Message
from .views_utils import get_anon_views_left, prefetch_votes
from .personalization import Personalizer
logger = logging.getLogger(__name__)

CONFIRMED_MSG = 'Confirmed'

class PostList(ListView):
    template_name = 'snips/post.html'
    model = Snip
    SNIPS_LIST = 'all_posts'
    PAGE_SIZE = 5
    NUM_IN_SESSION = 100
    SNIPS_KEY = 'snips_list'
    DESC = "Short Content, Decentralized platform"
    TITLE = "Snip - News. Summarized."

    def __init__(self, **kwargs):
        super(PostList, self).__init__()
        self.page = None
        self.session_ids = None
        self.is_scroll = False

    def is_scrolling(self):
        self.session_ids = self.load_session()
        self.page = self.request.GET.get('page')
        self.is_scroll = self.page and self.session_ids is not None
        return self.is_scroll

    def filter_liked(self, q):
        if self.request.GET.get('search'):
            return q

        if self.request.user.is_authenticated:
            if 'profile' in self.kwargs:
                q = q.filter(vote__user=self.request.user, vote__vote=SnipLog.LIKE)
            else:
                q = q.exclude(vote__user=self.request.user)
        return q

    def filter_main_post(self, q):
        if 'slug' in self.kwargs:
            q = q.exclude(slug=self.kwargs['slug'])
        return q

    def filter_category(self, q):
        if 'category' in self.kwargs:
            try:
                q = q.filter(category__name__iexact=self.kwargs['category'])
            except ValueError:
                q = Snip.objects.none()
        return q

    def search_or_personalize(self, q):
        if self.request.GET.get('search'):
            q = q.search(self.request.GET.get('search'), operator="or")
        else:
            if 'profile' in self.kwargs:
                q = q.order_by('-first_published_at')
            else:
                q = q.filter(show_in_main=True)
                personalizer = Personalizer(q, self.request.user)
                q = personalizer.personlize_feed()
        return q

    def get_queryset(self):
        q = super(PostList, self).get_queryset()
        if self.request.user.is_authenticated:
            Profile.objects.get_or_create(user=self.request.user)  # to make sure that the profile exists
        if self.is_scrolling():
            return q
        q = q.live()
        q = prefetch_votes(q, self.request.user)
        # TODO: check cases where liked and search
        q = self.filter_liked(q)
        q = self.filter_main_post(q)
        q = self.filter_category(q)
        q = self.search_or_personalize(q)
        return q

    def handle_existing_scroll(self, context):
        page = int(self.page)
        cur_ids = self.session_ids[(self.PAGE_SIZE * page):(self.PAGE_SIZE * (page + 1))]
        posts = Snip.objects.filter(id__in=cur_ids, live=True)
        posts = prefetch_votes(posts, self.request.user)
        posts_dict = {p.id: p for p in posts}
        context['posts'] = [posts_dict[id] for id in cur_ids]
        context['base_template'] = "snips/empty.html"
        if self.PAGE_SIZE * (page + 1) < len(self.session_ids):
            context['next_page'] = page + 1
        return context

    def is_subscribed(self):
        return self.request.user.is_authenticated and self.request.user.profile.subscribed

    def is_confirmed(self):
        msgs = get_messages(self.request)
        for m in msgs:
            if m.message == CONFIRMED_MSG:
                return True
        return False

    def handle_new_scroll(self, context):
        context['base_template'] = "snips/posts_wrapper.html"
        all_posts = context['object_list'][:self.NUM_IN_SESSION]
        if 'slug' in self.kwargs:
            try:
                main_post = prefetch_votes(Snip.objects.filter(slug=self.kwargs['slug']), self.request.user)[0]
                context['main_post'] = main_post
                context['page_title'] = main_post.title
                context['page_desc'] = shorten_text(main_post.body, 130)
                context['open_main_post'] = (main_post.is_locked != Snip.LOCKED or self.is_subscribed())
                all_posts = list(chain([main_post], all_posts))
            except IndexError as e:
                raise Http404('Post not found')
            if not context['main_post'].live:
                raise Http404('Post not found')
        else:
            context['page_title'] = self.TITLE
            context['page_desc'] = self.DESC

        self.create_session(all_posts)
        context['posts'] = all_posts[:self.PAGE_SIZE]

        # if not self.request.user.is_authenticated():
        #     context['views_left'] = get_anon_views_left(self.request)
        # else:
        context['views_left'] = 1000  # arbitrary
        context['my_messages'] = Message.objects.filter(live=True)

        context['categories'] = Category.objects.all()
        context[Vote.MARK_VOTE] = Vote.MARK_VOTE
        context[Vote.REMOVE_VOTE] = Vote.REMOVE_VOTE
        context['next_page'] = 1

        context['profile_view'] = 'profile' in self.kwargs
        context['confirmed'] = self.is_confirmed()

        self.set_referer()
        return context

    def get_context_data(self, **kwargs):
        context = super(PostList, self).get_context_data(**kwargs)
        if self.is_scroll:
            self.handle_existing_scroll(context)
        else:
            self.handle_new_scroll(context)
        self.add_metadata_to_posts(context['posts'])
        return context

    def add_metadata_to_posts(self, posts):
        for p in posts:
            p.liked = PostList.is_voted(p, SnipLog.LIKE)
            p.disliked = PostList.is_voted(p, SnipLog.DISLIKE)
            p.premium = self.is_premium(p)
        return posts

    def is_premium(self, post):
        user = self.request.user
        return post.is_locked == Snip.LOCKED and not (user.is_authenticated() and user.profile.subscribed)

    @staticmethod
    def is_voted(post, vote_type):
        try:
            if post.user_vote[0].vote == vote_type:
                return Vote.MARK_VOTE
        except (IndexError, AttributeError):
            pass
        return ''

    def create_session(self, posts):
        s = self.request.session
        posts_list = [p.id for p in posts]
        s[self.SNIPS_KEY] = json.dumps(posts_list)
        if not s.exists(s.session_key):
            s.create()

    def load_session(self):
        try:
            return json.loads(self.request.session[self.SNIPS_KEY])
        except KeyError:
            return None

    def set_referer(self):
        try:
            refer = self.request.META['HTTP_REFERER']
        except KeyError as e:
            return
        if self.request.get_host() in refer:
            return
        refer = refer[:Referer.MAX_URL_LENGTH]

        if self.request.user.is_authenticated():
            obj = Referer(user=self.request.user, referer=refer)
        else:
            obj = Referer(session=self.request.session.session_key, referer=refer)
        obj.save()


def confirmed(request):
    messages.info(request, CONFIRMED_MSG)
    return redirect('snips:posts')


