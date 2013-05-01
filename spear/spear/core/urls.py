from django.conf.urls.defaults import *
from django.views.generic.simple import redirect_to
from django.views.generic import TemplateView
import django.contrib.auth.views

urlpatterns = patterns('execmngr.views',
    (r'^$', TemplateView.as_view(template_name='core/home.html')),

    # Authentication
    url(r'', include('social_auth.urls')),
    url(r'^login/$', redirect_to, {'url': '/login/github'}),
    url(r'^logout/$', django.contrib.auth.views.logout, name='spear-core-logout'),
    #url(r'^profile/$', 'spear.core.views.profile'), # TODO: make first redirect to profile page 
)
