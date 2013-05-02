from django.core.urlresolvers import reverse
from django.views.generic.edit import FormView, DeleteView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from spear.execmngr.forms import NodeForm, SSHKeyForm
from spear.base.models import SSHKey

# TODO: 
# * fs navigation (view only)
# * task start/list
# * fs operations (edit)

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
    success_url = '/'
    template_name = 'execmngr/add_sshkey.html'
    
    def form_valid(self, form):
        sshkey = form.save(commit=False)
        sshkey.owner = self.request.user
        sshkey.save()
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
    
class NodeView(FormView):
    form_class = NodeForm
    success_url = '/'
    template_name = 'execmngr/add_node.html'
    
    def form_valid(self, form):
        form.save()
        return super(NodeView, self).form_valid(form)
    
