from django.db import models
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.models import User
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
    port = models.IntegerField(default=8042)
    user = models.TextField()
    executor_path = models.TextField()
    status = models.IntegerField(choices=STATUS_CHOICES, default=NONE)
    last_heartbeat = models.DateTimeField(default=datetime.datetime.now())
    description = models.TextField()
    sshkey = models.ForeignKey('SSHKey')
    owner = models.ForeignKey(User)

    def __unicode__(self):
        return self.user + u'@' + self.host

class SSHKey(models.Model):
    name = models.TextField()
    description = models.TextField()
    file = models.FileField(upload_to='sshkeys', storage=private_media)
    owner = models.ForeignKey(User)
    
    def __unicode__(self):
        return self.name

class Application(models.Model):
    name = models.TextField()
    registered = models.DateTimeField()
    owner = models.ForeignKey(User)

    def __unicode__(self):
        return self.name

class Repository(models.Model):
    SVN = 0
    GIT = 1
    FTP = 2
    TYPE_CHOICES = (
        (0, 'Subversion'),
        (1, 'Git'),
        (2, 'FTP'),
    )
    name = models.TextField()
    type = models.IntegerField(choices=TYPE_CHOICES, default=SVN)
    version = models.TextField()
    meta = models.TextField()
    registered = models.DateTimeField()
    owner = models.ForeignKey(User)

    def __unicode__(self):
        return self.name
    
class Installation(models.Model):
    node = models.ForeignKey(Node)
    installed = models.DateTimeField()
    app = models.ForeignKey(Application)
    repo = models.ForeignKey(Repository)
    
class Environment(models.Model):
    LOCAL = 0
    PBS = 1
    TYPE_CHOICES = (
        (0, 'Local'),
        (1, 'PBS'),
    )
    name = models.TextField()
    owner = models.ForeignKey(User)
    created = models.DateTimeField()
    type = models.IntegerField(choices=TYPE_CHOICES, default=LOCAL)
    meta = models.TextField()
    
    
class Configuration(models.Model):
    name = models.TextField()
    owner = models.ForeignKey(User)
    created = models.DateTimeField()
    app = models.ForeignKey(Application)
    app_version = models.TextField()
    app_meta = models.TextField()
    env_type = models.TextField()
    env_meta = models.TextField()
    in_files = models.TextField()
    out_files = models.TextField()
        
    def __unicode__(self):
        return self.name
    
class Task(models.Model):
    name = models.TextField()
    launched = models.DateTimeField()
    owner = models.ForeignKey(User)
    node = models.ForeignKey(Node, on_delete=models.CASCADE)
    env = models.ForeignKey(Environment)
    inst = models.ForeignKey(Installation)
    conf = models.ForeignKey(Configuration)
        
    status = models.IntegerField()
    exitstatus = models.IntegerField()
    workdir = models.TextField()
    executable = models.TextField()
    args = models.TextField()
    queue_type = models.TextField()
    queue_meta = models.TextField()
    stdin = models.TextField()
    stdout = models.TextField()
    stderr = models.TextField()
    last_retry = models.DateTimeField()
    gversion = models.IntegerField()
    