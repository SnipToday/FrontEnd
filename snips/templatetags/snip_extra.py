from django import template
from django.utils import timezone
from math import ceil
from snips.models import Snip, Vote

from .text_trunc import truncate_html

register = template.Library()

@register.filter
def to_html(value):
    return value.replace('\n\n', '\n').rstrip('\n').replace('\n', '<br>')


@register.filter
def is_post_locked(post):
    return post.is_locked == Snip.LOCKED


@register.simple_tag
def is_cat_selected(cur_category, request):
    return str(cur_category.id) == request.GET.get('category')


@register.simple_tag
def split_text(text):
    num_words = 25
    first, second = truncate_html(text, num_words, words=True)
    return first, second

@register.simple_tag
def get_page_field(main_post, field, def_val):
    return getattr(main_post, field, def_val)

@register.simple_tag
def url_without_paging(request, field):
    get = request.GET.copy()
    try:
        del get[field]
    except KeyError:
        pass
    return get.urlencode()

@register.filter
def age(value):
    now = timezone.now()
    try:
        diff = (now - value).total_seconds() / 3600
        if diff < 1:
            diff = ceil(diff * 60)
            if diff == 1:
                return "A minute ago"
            return "%s minutes ago" % diff
        elif diff < 23:
            diff = ceil(diff)
            if diff == 1:
                return "An hour ago"
            return "%s hours ago" % diff
        else:
            return value.strftime('%m/%d/%Y, %H:00 UTC')
    except Exception:
        return ''


