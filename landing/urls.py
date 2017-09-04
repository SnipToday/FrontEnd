from django.conf.urls import url, include
from . import views


app_name = 'landing'

urlpatterns = [
    url(r'^terms/$', views.terms, name='terms'),
    url(r'^privacy_policy/$', views.privacy, name='privacy'),
]


