from django.conf.urls.defaults import *
from spear.fs.views import nav

urlpatterns = patterns('execmngr.views',
    url(r'^nav/(?P<node_pk>\d+)/(?P<path>.*)$', nav, name='spear-fs-nav'),
)
