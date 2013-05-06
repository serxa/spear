from django.conf.urls.defaults import *
from spear.execmngr.views import SSHKeyView, SSHKeyDelete, SSHKeyList, SSHKeyDetail
from spear.execmngr.views import NodeView, NodeList, NodeDetail, NodeDelete
from spear.execmngr.views import heartbeat

urlpatterns = patterns('execmngr.views',
    # Node related
    url(r'^list_nodes/$', NodeList.as_view(), name='spear-execmngr-list_nodes'),
    url(r'^node/(?P<pk>\d+)/$', NodeDetail.as_view(), name='spear-execmngr-node'),
    url(r'^add_node/$', NodeView.as_view(), name='spear-execmngr-add_node'),
    url(r'^delete_node/(?P<pk>\d+)/$', NodeDelete.as_view(), name='spear-execmngr-delete_node'),

    # SSH key related
    url(r'^list_sshkeys/$', SSHKeyList.as_view(), name='spear-execmngr-list_sshkeys'),
    url(r'^sshkey/(?P<pk>\d+)/$', SSHKeyDetail.as_view(), name='spear-execmngr-sshkey'),
    url(r'^add_sshkey/$', SSHKeyView.as_view(), name='spear-execmngr-add_sshkey'),
    url(r'^delete_sshkey/(?P<pk>\d+)/$', SSHKeyDelete.as_view(), name='spear-execmngr-delete_sshkey'),
                       
    url(r'^hb/(?P<node_id>\d+)/$', 'heartbeat'),
    #(r'^start/$', 'start'),
    #(r'^stop/$', 'stop'),
    #(r'^remove_node/$', 'remove_node'),
)
