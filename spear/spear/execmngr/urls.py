from django.conf.urls.defaults import *
from spear.execmngr.views import SSHKeyView, SSHKeyDelete, SSHKeyList, SSHKeyDetail
from spear.execmngr.views import NodeView, NodeList, NodeDetail, NodeDelete
from spear.execmngr.views import TaskList, TaskDetail, TaskStart, TaskStop, TaskDelete
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
                       
    # Task management
    url(r'^list_tasks/$', TaskList.as_view(), name='spear-execmngr-list_tasks'),
    url(r'^task/(?P<pk>\d+)/$', TaskDetail.as_view(), name='spear-execmngr-task'),
    url(r'^start_task/$', TaskStart.as_view(), name='spear-execmngr-start_task'),
    url(r'^stop_task/(?P<pk>\d+)/$', TaskStop.as_view(), name='spear-execmngr-stop_task'),
    url(r'^delete_task/(?P<pk>\d+)/$', TaskDelete.as_view(), name='spear-execmngr-delete_task'),

    url(r'^hb/(?P<node_id>\d+)/$', 'heartbeat'),
)
