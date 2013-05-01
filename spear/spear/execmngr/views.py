from django.views.generic.edit import FormView, DeleteView
from spear.execmngr.forms import NodeForm, SSHKeyForm
from spear.base.models import SSHKey

# TODO: 
# * registration
# * authentication
# * fs navigation (view only)
# * task start/list
# * authorization/permissions
# * fs operations (edit)


class SSHKeyView(FormView):
    form_class = SSHKeyForm
    success_url = '/'
    template_name = 'execmngr/add_sshkey.html'
    
    def form_valid(self, form):
        form.save()
        return super(SSHKeyView, self).form_valid(form)

class SSHKeyDelete(DeleteView):
    model = SSHKey
    success_url = '/execmngr/list_sshkeys/' #reverse_lazy('list_sshkeys')
    template_name = 'execmngr/delete_sshkey.html' 
    
class NodeView(FormView):
    form_class = NodeForm
    success_url = '/'
    template_name = 'execmngr/add_node.html'
    
    def form_valid(self, form):
        form.save()
        return super(NodeView, self).form_valid(form)
    
