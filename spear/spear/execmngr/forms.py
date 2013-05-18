from django.forms import ModelForm
from spear.base.models import Node, SSHKey, Task

class NodeForm(ModelForm):
    class Meta:
        model = Node
        fields = ('host', 'user', 'description', 'sshkey')

class SSHKeyForm(ModelForm):
    class Meta:
        model = SSHKey
        fields = ('name', 'description', 'file')

class TaskStartForm(ModelForm):
    class Meta:
        model = Task
        fields = ('node', 'workdir', 'executable', 'args', 'stdin', 'stdout', 'stderr')
    