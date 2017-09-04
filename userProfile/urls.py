from django.conf.urls import url, include
from . import views


app_name = 'userProfile'

urlpatterns = [
    url(r'^subscribe/$', views.subscribe, name='subscribe'),
    url(r'^pay_return/$', views.paypal_pay_return, name='pay-return'),
    url(r'^pay_cancel/$', views.paypal_pay_cancel, name='pay-cancel'),
    url(r'^log/$', views.log_view, name='user-log'),
    url(r'^update_wallet/$', views.update_wallet, name='update-wallet'),
]


