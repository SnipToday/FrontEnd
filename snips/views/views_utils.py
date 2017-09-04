from datetime import timedelta

from django.db.models import Prefetch
from django.utils import timezone
from ..models import SnipLog, Vote

MAX_POST_IN_PERIOD = 10
PERIOD = 30


def prefetch_votes(q, user):
    if user.is_authenticated():
        q = q.prefetch_related(
            Prefetch("vote_set", queryset=Vote.objects.filter(user=user), to_attr="user_vote"))
    return q


def get_anon_views_left(request):
    min_age = timezone.now() - timedelta(days=PERIOD)
    num_viewed = SnipLog.objects.filter(session=request.session.session_key, action=SnipLog.READ_MORE,
                                        date__gte=min_age).count()
    return MAX_POST_IN_PERIOD - num_viewed