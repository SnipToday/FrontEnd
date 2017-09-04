import logging
from math import exp

from django.utils import timezone
from .views_utils import prefetch_votes
from ..models import Snip, SnipLog, Vote, PostMetrics

logger = logging.getLogger(__name__)

class Personalizer(object):
    UP_VOTES = 'UP'
    ATTITUDE = 'ATT'
    COUNT = 'COUNT'
    MIN_VOTES = 6
    MIN_CATEFORY_VOTES = 4

    def __init__(self, snips, user):
        self.snips = snips
        self.user = user

    def prepare_snips_metrics(self):
        self.snips = self.snips.prefetch_related('postmetrics')
        self.calc_age_factor()
        self.snips = self.calc_snips_popularity(self.snips)
        self.snips = list(self.snips)

    def personlize_feed(self):
        self.prepare_snips_metrics()
        if self.user.is_authenticated():
            user_attitude = self.get_user_attitude_to_categories()
            if self.user.profile.subscribed:
                new_order = self.build_subscriber_snips_list(user_attitude)
            else:
                new_order = self.build_non_subscriber_snips_list(user_attitude)
        else:
            new_order = self.build_guest_snip_list()
        return new_order

    def build_subscriber_snips_list(self, user_attitude):
        return self.build_snips_list(self.snips, user_attitude)

    def build_non_subscriber_snips_list(self, user_attitude):
        return self.build_free_locked_list(user_attitude)

    def build_guest_snip_list(self):
        return self.build_free_locked_list(None)

    @staticmethod
    def merge_lists(list_a, list_b):
        merge_list = []
        for i in range(max(len(list_a), len(list_b))):
            try:
                merge_list.append(list_a[i])
            except IndexError:
                pass
            try:
                merge_list.append(list_b[i])
            except IndexError:
                pass
        return merge_list

    def build_free_locked_list(self, user_attitude):
        locked_snips = self.build_snips_list([s for s in self.snips if s.is_locked == Snip.LOCKED], user_attitude)
        free_snips = self.build_snips_list([s for s in self.snips if s.is_locked == Snip.FREE], user_attitude)
        return self.merge_lists(free_snips, locked_snips)

    @staticmethod
    def calc_snip_grade_with_att(snips, attitude):
        category_att, total_att = attitude
        for s in snips:
            if s.category in category_att and category_att[s.category][Personalizer.COUNT] > Personalizer.MIN_CATEFORY_VOTES:
                s.grade = category_att[s.category][Personalizer.ATTITUDE]
            else:
                s.grade = total_att[Personalizer.ATTITUDE]
        return snips

    @staticmethod
    def build_snips_list(snips, attitude):
        NO_ATT_GRADE = 1
        if attitude:
            snips = Personalizer.calc_snip_grade_with_att(snips, attitude)
        return sorted(snips, key=lambda x: x.popularity * x.age_factor * getattr(x, 'grade', NO_ATT_GRADE), reverse=True)

    def calc_age_factor(self):
        now = timezone.now()
        for s in self.snips:
            age_days = (now - s.first_published_at).total_seconds() / (60*60*24)
            s.age_factor = 1 - exp(-1.0 / (1.2 * s.death_factor * age_days ** s.death_factor)) # TODO decide about the scale factor 1.2
            if s.age_factor < 0:
                logger.error('Age factor is negative for snip - %s' % s.id)

    @staticmethod
    def check_post_metrics_exists(s):
        try:
            s.postmetrics
        except PostMetrics.DoesNotExist:
            s.postmetrics = PostMetrics.objects.create(snip=s)

    @staticmethod
    def calc_snips_popularity(snips):
        default_popularity = 0.8  # TODO replace with average popularity of posts - calc it up front
        min_snip_votes = 5
        for s in snips:
            Personalizer.check_post_metrics_exists(s)
            if s.postmetrics.like + s.postmetrics.dislike < min_snip_votes:
                s.popularity = default_popularity
            else:
                s.popularity = s.postmetrics.like / (s.postmetrics.like + s.postmetrics.dislike)
        return snips

    def get_user_attitude_to_categories(self):
        categories_att = {}
        voted_snips = prefetch_votes(Snip.objects.filter(vote__user=self.user), self.user)
        voted_snips = Personalizer.calc_snips_popularity(voted_snips.prefetch_related('postmetrics'))
        total_att = {self.UP_VOTES: 0, self.COUNT: len(voted_snips)}
        if len(voted_snips) < self.MIN_VOTES:
            return None
        for s in voted_snips:
            cur_up = s.popularity * (s.user_vote[0].vote == SnipLog.LIKE)
            if s.category in categories_att:
                categories_att[s.category][self.UP_VOTES] += cur_up
                categories_att[s.category][self.COUNT] += 1
            else:
                categories_att[s.category] = {self.UP_VOTES: cur_up, self.COUNT: 1}
            total_att[self.UP_VOTES] += cur_up
        for value in categories_att.values():
            value[self.ATTITUDE] = value[self.UP_VOTES] * 1.0 / value[self.COUNT]
        total_att[self.ATTITUDE] = total_att[self.UP_VOTES] * 1.0 / total_att[self.COUNT]
        return categories_att, total_att


