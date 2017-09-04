import os

from django.contrib.auth.decorators import login_required
from django.forms import ModelForm
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.http import require_GET
from paypal.standard.forms import PayPalPaymentsForm
from django.conf import settings
from .models import UserLog, Wallet

class MyPayPal(PayPalPaymentsForm):
    def get_image(self):
        return "https://www.paypalobjects.com/webstatic/en_US/i/buttons/checkout-logo-medium.png"


def get_button_data(request, price, period, item_name):
    PAYPAL_EMAIL = os.environ.get('PAYPAL_EMAIL')
    CANCEL_URL = 'http://' + request.META['HTTP_HOST'] + reverse('userProfile:pay-cancel')
    NOTIFY_URL = 'http://' + request.META['HTTP_HOST'] + reverse('paypal-ipn')
    if settings.DEBUG:
        NOTIFY_URL = 'http://' + '109.67.151.10' + reverse('paypal-ipn')
    RETURN_URL = 'http://' + request.META['HTTP_HOST'] + reverse('userProfile:pay-return')

    basic_button = {
        "cmd": "_xclick-subscriptions",
        "business": PAYPAL_EMAIL,
        "a3": price,
        "p3": "1",
        "t3": period,
        "custom": request.user.id,
        "src": '1',
        "item_name": item_name,
        "currency_code": 'USD',
        "lc": "en_US",
        "no_note": "1",
        "cancel_return": CANCEL_URL,
        "notify_url": NOTIFY_URL,
        "return_url": RETURN_URL,
    }
    return basic_button


@login_required
def subscribe(request):
    return base_subscribe(request)


def base_subscribe(request, payment_failed=False):
    yearly_price = 1.95
    monthly_price = 2.95
    yearly_button = get_button_data(request, str(yearly_price*12), 'Y', 'Snip Yearly')
    monthly_button = get_button_data(request, str(monthly_price), 'M', 'Snip Monthly')
    yearly_form = MyPayPal(initial=yearly_button)
    monthly_form = MyPayPal(initial=monthly_button)
    context = {'paypal_yearly': [yearly_price, yearly_form], 'paypal_monthly': [monthly_price, monthly_form],
               'payment_failed': payment_failed}
    return render(request, 'userProfile/subscribe.html', context)


@require_GET
def paypal_pay_return(request):
    return redirect('snips:posts')


def paypal_pay_cancel(request):
    return base_subscribe(request, payment_failed=True)


def set_action_user_params(request, dict):
    if request.user.is_authenticated():
        dict['user'] = request.user
    else:
        dict['session'] = request.session.session_key


def get_action_additional_params(request, param):
    try:
        param['param1'] = request.POST['param1']
    except KeyError:
        pass
    try:
        param['param2'] = request.POST['param2']
    except KeyError:
        pass
    return param


def log_view(request):
    if request.method != 'POST':
        return JsonResponse({'message': 'Not Post Method'}, status=500)
    try:
        action = request.POST['action']
    except KeyError:
        return JsonResponse({'message': 'Failed to get action'}, status=404)

    action_dict = {'action': action}
    set_action_user_params(request, action_dict)
    get_action_additional_params(request, action_dict)
    UserLog.objects.create(**action_dict)
    return JsonResponse({'message': 'success'})


class WalletForm(ModelForm):
    class Meta:
        model = Wallet
        exclude = ['user']


@login_required
def update_wallet(request):
    if request.method == 'POST':
        wallet, created = Wallet.objects.get_or_create(user=request.user)
        form = WalletForm(request.POST, instance=wallet)
        if form.is_valid():
            form.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

