import sys
import json
import datetime
from django.core.urlresolvers import reverse
from django.views.generic.edit import FormView, DeleteView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from spear.execmngr.forms import NodeForm, SSHKeyForm, TaskStartForm
from spear.base.models import SSHKey, Node, Task
from django.http import Http404, HttpResponse
from django.views.decorators.csrf import csrf_exempt

#
# Views for SSH Key 
#
class SSHKeyList(ListView):
    model = SSHKey
    paginate_by = 5
    context_object_name = 'sshkeys'
    template_name = 'execmngr/list_sshkeys.html'
            
    def get_queryset(self):
        return SSHKey.objects.filter(owner=self.request.user)
        
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(SSHKeyList, self).dispatch(*args, **kwargs)

class SSHKeyDetail(DetailView):
    model = SSHKey
    template_name = 'execmngr/sshkey.html'
    context_object_name = 'sshkey'

    def get_queryset(self):
        return SSHKey.objects.filter(owner=self.request.user)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(SSHKeyDetail, self).dispatch(*args, **kwargs)

class SSHKeyView(FormView):
    form_class = SSHKeyForm
    template_name = 'execmngr/add_sshkey.html'

    def get_success_url(self):
        return reverse('spear-execmngr-sshkey', kwargs={'pk': self.sshkey.id})
    
    def form_valid(self, form):
        self.sshkey = form.save(commit=False)
        self.sshkey.owner = self.request.user
        self.sshkey.save()
        return super(SSHKeyView, self).form_valid(form)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(SSHKeyView, self).dispatch(*args, **kwargs)

class SSHKeyDelete(DeleteView):
    model = SSHKey
    template_name = 'execmngr/delete_sshkey.html'
    context_object_name = 'sshkey' 

    def get_success_url(self):
        return reverse('spear-execmngr-list_sshkeys')

    def get_queryset(self):
        return SSHKey.objects.filter(owner=self.request.user)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(SSHKeyDelete, self).dispatch(*args, **kwargs)
    
#
# Views for Nodes 
#
class NodeList(ListView):
    model = Node
    paginate_by = 5
    context_object_name = 'nodes'
    template_name = 'execmngr/list_nodes.html'
            
    def get_queryset(self):
        return Node.objects.filter(owner=self.request.user)
        
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(NodeList, self).dispatch(*args, **kwargs)

class NodeDetail(DetailView):
    model = Node
    template_name = 'execmngr/node.html'
    context_object_name = 'node'

    def get_queryset(self):
        return Node.objects.filter(owner=self.request.user)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(NodeDetail, self).dispatch(*args, **kwargs)

class NodeView(FormView):
    form_class = NodeForm
    template_name = 'execmngr/add_node.html'

    def get_success_url(self):
        return reverse('spear-execmngr-node', kwargs={'pk': self.node.id})
    
    def get_form(self, form_class):
        form = super(NodeView, self).get_form(form_class)
        form.fields["sshkey"].queryset=SSHKey.objects.filter(owner=self.request.user)
        return form
    
    def form_valid(self, form):
        self.node = form.save(commit=False)
        self.node.owner = self.request.user
        self.node.save()
        return super(NodeView, self).form_valid(form)
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(NodeView, self).dispatch(*args, **kwargs)

class NodeDelete(DeleteView):
    model = Node
    template_name = 'execmngr/delete_node.html'
    context_object_name = 'node' 

    def get_success_url(self):
        return reverse('spear-execmngr-list_nodes')

    def get_queryset(self):
        return Node.objects.filter(owner=self.request.user)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(NodeDelete, self).dispatch(*args, **kwargs)

#
# Views for Tasks 
#
class TaskList(ListView):
    model = Task
    paginate_by = 5
    context_object_name = 'tasks'
    template_name = 'execmngr/list_tasks.html'
            
    def get_queryset(self):
        return Task.objects.filter(owner=self.request.user)
        
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(TaskList, self).dispatch(*args, **kwargs)

class TaskDetail(DetailView):
    model = Task
    template_name = 'execmngr/task.html'
    context_object_name = 'task'

    def get_queryset(self):
        return Task.objects.filter(owner=self.request.user)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(TaskDetail, self).dispatch(*args, **kwargs)

class TaskStart(FormView):
    form_class = TaskStartForm
    template_name = 'execmngr/start_task.html'

    def get_success_url(self):
        return reverse('spear-execmngr-task', kwargs={'pk': self.task.id})
    
    def get_form(self, form_class):
        form = super(TaskStart, self).get_form(form_class)
        form.fields["node"].queryset=Node.objects.filter(owner=self.request.user)
        return form
    
    def form_valid(self, form):
        self.task = form.save(commit=False)
        self.task.owner = self.request.user
        self.task.status = Task.STARTING
        self.task.queue_type = Task.NONE
        self.task.gversion = 0
        self.task.save()
        return super(TaskStart, self).form_valid(form)
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(TaskStart, self).dispatch(*args, **kwargs)

class TaskStop(FormView):
    pass

class TaskDelete(DeleteView):
    model = Task
    template_name = 'execmngr/delete_task.html'
    context_object_name = 'task' 

    def get_success_url(self):
        return reverse('spear-execmngr-list_tasks')

    def get_queryset(self):
        return Task.objects.filter(owner=self.request.user)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(TaskDelete, self).dispatch(*args, **kwargs)

def json_response(json_data):
    return HttpResponse(json.dumps(json_data), mimetype="application/json") 

@csrf_exempt
def heartbeat(request, node_id):
    if request.method != "POST":
        raise Http404
    try:
        node = Node.objects.get(pk=node_id)
    except Node.DoesNotExist:
        return json_response({ 'success': False, 'error': 'node {0} does not exist'.format(node_id) })
    
    try:
        request_json = json.loads(request.raw_post_data)
        node.port = request_json['port']
        node.last_heartbeat = datetime.datetime.now()
        node.save()
        return json_response({ 'success': True })
    except:
        e = sys.exc_info()[1]
        return json_response({ 'success': False, 'error': repr(e) })
         
