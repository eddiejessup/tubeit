from django.conf.urls import patterns, url
from map.views import search, draw
from map.models import *

urlpatterns = patterns('map.views',
    url(r'^search/$', search, name='search'),
    url(r'^draw/$', draw, name='draw'),
)
