from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from model_utils import Choices
from paypal.standard.ipn.models import PayPalIPN
from simple_history.models import HistoricalRecords


class Profile(models.Model):
    user = models.OneToOneField(User)
    subscribed = models.BooleanField(default=False)
    subscription_date = models.DateTimeField(blank=True, null=True)
    paypal = models.ForeignKey(PayPalIPN, on_delete=models.SET_NULL, blank=True, null=True)


class Wallet(models.Model):
    user = models.OneToOneField(User)
    eth_address = models.CharField(max_length=70, blank=True, null=True)

    def __str__(self):
        return '%s' % self.eth_address

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


class SessionToUser(models.Model):
    session = models.CharField(max_length=32)
    user = models.ForeignKey(User)
    date = models.DateTimeField(auto_now_add=True)


class AbstractOwner(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, db_index=True)
    session = models.CharField(max_length=32, null=True, blank=True, db_index=True)

    class Meta:
        abstract = True


class UserLog(AbstractOwner):
    SIGNIN = 'signin'
    SIGNUP = 'signup'
    SUBSCRIBE = 'subscribe'
    SEARCH = 'search'
    PROFILE = 'profile'
    FOLLOW = 'follow'
    LOG_ACTIONS = Choices(SIGNIN, SIGNUP, SUBSCRIBE, SEARCH, PROFILE, FOLLOW)

    action = models.CharField(max_length=15, choices=LOG_ACTIONS, verbose_name='action')
    param1 = models.CharField(max_length=100, null=True, blank=True)
    param2 = models.CharField(max_length=100, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True, verbose_name='date')

    class Meta:
        ordering = ['-date']