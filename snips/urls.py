from django.conf.urls import url

from . import views

app_name = 'snips'

urlpatterns = [
    url(r'^$', views.PostList.as_view(), name='posts'),
    url(r'^category/(?P<category>[\w-]+)/$', views.PostList.as_view(), name='posts_category'),
    url(r'^confirmed/$', views.confirmed, name='confirmed'),
    url(r'^post/(?P<slug>[\w-]+)/$', views.PostList.as_view(), name='post'),
    url(r'^category/(?P<category>[\w-]+)/post/(?P<slug>[\w-]+)/$', views.PostList.as_view(), name='post_category'),
    url(r'^profile/$', views.PostList.as_view(), {'profile': True}, name='profile'),
    url(r'^snip_log/(?P<snip_id>[0-9]+)/$', views.log_view, name='log'),
    url(r'^user-autocomplete/$', views.UserAutocomplete.as_view(), name='user-autocomplete'),
]


