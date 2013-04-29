from django.conf.urls.defaults import *
from django.views.generic import TemplateView

urlpatterns = patterns('execmngr.views',
    (r'^$', TemplateView.as_view(template_name='core/home.html')),
)
