from django.conf.urls.defaults import *
from django.views.generic.simple import redirect_to
from django.views.generic import TemplateView
import django.contrib.auth.views

urlpatterns = patterns('',
    (r'^$', TemplateView.as_view(template_name='core/home.html')),

    # Authentication
    url(r'^login/$', 'spear.core.views.login', name='spear-core-login'),
    url(r'', include('social_auth.urls')),
    #url(r'^login/$', TemplateView.as_view(template_name='core/login.html'), name='spear-core-login'),
    url(r'^login-error/$', TemplateView.as_view(template_name='core/login-error.html')),
    url(r'^logout/$', django.contrib.auth.views.logout, name='spear-core-logout'),
    #url(r'^profile/$', 'spear.core.views.profile'), # TODO: make first redirect to profile page
)
