
import logging
import os

from allauth.account.signals import user_signed_up
from django.core.mail import send_mail
from django.dispatch import receiver
from django.utils import timezone
from paypal.standard.ipn.signals import valid_ipn_received

from django.conf import settings
from .models import Profile, SessionToUser
from .payment_check import check_payment


logger = logging.getLogger(__name__)


@receiver(valid_ipn_received)
def show_me_the_money(sender, **kwargs):
    ipn_obj = sender
    if not ipn_obj.custom and not settings.DEBUG:
        send_mail(
            'Missing IPN user id',
            'IPN_obj - %s' % ipn_obj,
            settings.SERVER_EMAIL,
            [settings.ADMINS[0][1]],
            fail_silently=False,
        )
    if ipn_obj.txn_type == 'subscr_signup' and check_payment(ipn_obj):
        try:
            p = Profile.objects.get(user__id=ipn_obj.custom)
            p.subscribed = True
            p.paypal = ipn_obj
            p.subscription_date = timezone.now()
            p.save()
        except Profile.DoesNotExist as e:
            logger.exception('User ID does not exist - %s' % ipn_obj.custom)


@receiver(user_signed_up)
def connect_session_user(sender, request, user, **kwargs):
    if request.session.session_key:
        from mixpanel import Mixpanel
        try:
            mp = Mixpanel(os.environ.get('MIXPANEL_TOKEN'))
            mp.alias(user.email, request.session.session_key)
            mp.people_set(user.email, {
                '$first_name': user.first_name,
                '$last_name': user.last_name,
                '$email': user.email,
            })
            mp.track(user.email, 'signup', {'user_create': True})
        except Exception as e:
            logger.exception('Mixpanel Error - %s' % e)
        SessionToUser.objects.create(user=user, session=request.session.session_key)