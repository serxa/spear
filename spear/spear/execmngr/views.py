from django.core.urlresolvers import reverse
from django.views.generic.edit import FormView, DeleteView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from spear.execmngr.forms import NodeForm, SSHKeyForm
from spear.base.models import SSHKey, Node

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
