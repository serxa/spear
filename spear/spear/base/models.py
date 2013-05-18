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
        (NONE, 'None'),
        (INSTALLING, 'Installing'),
        (INSTALLED, 'Installed'),
        (STARTING, 'Starting'),
        (RUNNING, 'Running'),
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
    registered = models.DateTimeField(default=datetime.datetime.now())
    owner = models.ForeignKey(User)

    def __unicode__(self):
        return self.name

class Repository(models.Model):
    SVN = 0
    GIT = 1
    FTP = 2
    TYPE_CHOICES = (
        (SVN, 'Subversion'),
        (GIT, 'Git'),
        (FTP, 'FTP'),
    )
    name = models.TextField()
    registered = models.DateTimeField(default=datetime.datetime.now())
    owner = models.ForeignKey(User)
    type = models.IntegerField(choices=TYPE_CHOICES, default=SVN)
    app = models.ForeignKey(Application)
    version = models.TextField()
    meta = models.TextField()

    def __unicode__(self):
        return self.name
    
class Installation(models.Model):
    node = models.ForeignKey(Node)
    installed = models.DateTimeField(default=datetime.datetime.now())
    repo = models.ForeignKey(Repository)
    
class Environment(models.Model):
    LOCAL = 0
    PBS = 1
    TYPE_CHOICES = (
        (LOCAL, 'Local'),
        (PBS, 'PBS'),
    )
    name = models.TextField()
    owner = models.ForeignKey(User)
    created = models.DateTimeField(default=datetime.datetime.now())
    type = models.IntegerField(choices=TYPE_CHOICES, default=LOCAL)
    meta = models.TextField()
    
    
class Configuration(models.Model):
    name = models.TextField()
    owner = models.ForeignKey(User)
    created = models.DateTimeField(default=datetime.datetime.now())
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
    NONE = ''
    QUEUE_TYPE_CHOICES = (
        (NONE, 'Do not use queue'),
    )

    STARTING = 0
    ENQUEUED = 1
    RUNNING = 2
    STOPPING = 3
    ABORTED = 4
    FINISHED = 5
    STATUS_CHOICES = (
        (STARTING, 'Starting'),
        (ENQUEUED, 'Enqueued'),
        (RUNNING, 'Running'),
        (STOPPING, 'Stopping'),
        (ABORTED, 'Aborted'),
        (FINISHED, 'Finished'),
    )

    launched = models.DateTimeField(default=datetime.datetime.now())
    owner = models.ForeignKey(User)
    node = models.ForeignKey(Node, on_delete=models.CASCADE)
    env = models.ForeignKey(Environment, null=True)
    inst = models.ForeignKey(Installation, null=True)
    conf = models.ForeignKey(Configuration, null=True)
        
    status = models.IntegerField()
    exitstatus = models.IntegerField(null=True)
    workdir = models.TextField()
    executable = models.TextField()
    args = models.TextField(blank=True)
    queue_type = models.TextField(choices=QUEUE_TYPE_CHOICES)
    queue_meta = models.TextField(blank=True)
    stdin = models.TextField(default='/dev/null', blank=True)
    stdout = models.TextField(default='/dev/null', blank=True)
    stderr = models.TextField(default='/dev/null', blank=True)
    last_retry = models.DateTimeField(default=datetime.datetime.now())
    gversion = models.IntegerField()
    