"""btp_web URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include,url
from django.contrib import admin
from django.conf.urls import patterns,include,url
# from book import views

app_name = 'book'

urlpatterns = patterns('',
   url(r'^book/$', 'book.views.index', name='index'),
   url(r'^send/', 'book.views.send', name='send_data'),
   # url(r'^login/$', 'book.views.login', name='login'),
   url(r'^admin/',include(admin.site.urls)),
   url(r'^genre_opp/','book.views.genre_opp', name='genre_opp'),
   url(r'^collab/','book.views.collab', name='collab'),
   url(r'^editor/','book.views.editor', name='editor'),
   url(r'^remaining/', 'book.views.remain', name='remain'),
   url(r'^genre/', 'book.views.genre', name='genre'),
   url(r'^page/', 'book.views.page', name='page'),
   url(r'^all/', 'book.views.all', name='all'),
   url(r'^age/', 'book.views.age', name='age'),
   url('', include('social_django.urls', namespace='social')),
   url('', include('django.contrib.auth.urls', namespace='auth')),
   url(r'^precision/','book.views.precision', name='precision'),
   url(r'^prcurve/','book.views.pr_curve', name='pr_curve'),
   url(r'^mae/','book.views.mae', name='mae')
   # url(r'^register-by-token/(?P<backend>[^/]+)/$','djauthapp.views.register_by_access_token')
)
