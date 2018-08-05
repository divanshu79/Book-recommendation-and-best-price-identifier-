from django.conf.urls import patterns,include,url
from . import views

app_name = 'book'

urlpatterns = patterns('',
   url(r'^$', 'book.views.index', name='index'),
   url(r'^login/$', 'book.views.login', name='login'),
   url(r'^book/', 'book.views.index', name='index'),
   # url(r'^at/$', 'djauthapp.views.register_by_access_token', name='register')
   url(r'^genre_opp/','views.genre_opp', name='genre_opp'),
   url(r'^genre/','views.genre', name='genre'),
   url('', include('social_django.urls', namespace='social')),
   url('', include('django.contrib.auth.urls', namespace='auth')),
   # url(r'^register-by-token/(?P<backend>[^/]+)/$','djauthapp.views.register_by_access_token')
)