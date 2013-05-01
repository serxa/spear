from django.db import models
from django.core.files.storage import FileSystemStorage
import datetime
from spear import settings

private_media = FileSystemStorage(location=settings.PRIVATE_MEDIA_ROOT)

# Create your models here.
class Node(models.Model):
    NONE = 0
    INSTALLING = 1
    INSTALLED = 2
    STARTING = 3
    RUNNING = 4
    STATUS_CHOICES = (
        (0, 'None'),
        (1, 'Installing'),
        (2, 'Installed'),
        (3, 'Starting'),
        (4, 'Running'),
    )
    host = models.TextField()
    port = models.IntegerField(default=8013)
    user = models.TextField()
    executor_path = models.TextField()
    status = models.IntegerField(choices=STATUS_CHOICES, default=NONE)
    last_heartbeat = models.DateTimeField(default=datetime.datetime.now())
    description = models.TextField()
    sshkey = models.ForeignKey('SSHKey')

    def __unicode__(self):
        return self.user + u'@' + self.host

class SSHKey(models.Model):
    name = models.TextField()
    description = models.TextField()
    file = models.FileField(upload_to='sshkeys', storage=private_media)
    #user = models.ForeignKey('User')
    
    def __unicode__(self):
        return self.name

class Task(models.Model):
    nid = models.ForeignKey(Node, on_delete=models.CASCADE)
    status = models.IntegerField()
    queue_type = models.TextField()
    exitstatus = models.IntegerField()
    workdir = models.TextField()
    executable = models.TextField()
    args = models.TextField()
    queue_conf = models.TextField()
    stdin = models.TextField()
    stdout = models.TextField()
    stderr = models.TextField()
    last_retry = models.DateTimeField()
    gversion = models.IntegerField()
    