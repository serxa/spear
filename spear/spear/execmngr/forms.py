from django.forms import ModelForm
from spear.base.models import Node, SSHKey

class NodeForm(ModelForm):
    class Meta:
        model = Node
        fields = ('host', 'user', 'description', 'sshkey')

class SSHKeyForm(ModelForm):
    class Meta:
        model = SSHKey
    