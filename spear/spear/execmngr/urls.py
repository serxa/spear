from django.conf.urls.defaults import *
from django.views.generic import ListView, DetailView
from views import NodeView, SSHKeyView
from spear.base.models import Node, SSHKey 
from spear.execmngr.views import SSHKeyDelete

urlpatterns = patterns('execmngr.views',
    url(r'^add_node/$', NodeView.as_view(), name='spear-execmngr-add_node'),
    url(r'^node/(?P<pk>\d+)/$', DetailView.as_view(
            context_object_name='node',
            model=Node,
            template_name='execmngr/node.html',
        ), name='spear-execmngr-node'),
    url(r'^list_nodes/$', ListView.as_view(
            model = Node,
            paginate_by = 5,
            context_object_name = 'nodes',
            queryset = Node.objects.all(),
            template_name='execmngr/list_nodes.html')
        , name='spear-execmngr-list_nodes'),

    url(r'^add_sshkey/$', SSHKeyView.as_view(), name='spear-execmngr-add_sshkey'),
    url(r'^delete_sshkey/(?P<pk>\d+)/$', SSHKeyDelete.as_view(context_object_name='sshkey'), name='spear-execmngr-delete_sshkey'),
    url(r'^sshkey/(?P<pk>\d+)/$', DetailView.as_view(
            context_object_name='sshkey',
            model=SSHKey,
            template_name='execmngr/sshkey.html',
        ), name='spear-execmngr-sshkey'),
    url(r'^list_sshkeys/$', ListView.as_view(
            model = SSHKey,
            paginate_by = 5,
            context_object_name = 'sshkeys',
            queryset = SSHKey.objects.all(),
            template_name='execmngr/list_sshkeys.html')
        , name='spear-execmngr-list_sshkeys'),
                       
    #(r'^hb/$', 'hb'),
    #(r'^start/$', 'start'),
    #(r'^stop/$', 'stop'),
    #(r'^remove_node/$', 'remove_node'),
)
