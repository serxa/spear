import sys
import httplib
import urllib
import json
import socket
import os.path
from django.core.urlresolvers import reverse
from django.shortcuts import render
from spear.base.models import Node
from spear import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

@login_required
def nav(request, node_pk, path):
    path = os.path.normpath(os.path.join('/', urllib.unquote(path)))
    ctx = { 'success': False, 'path': path  }
    try:
        node = Node.objects.get(pk=node_pk)
        if node.owner != request.user:
            return render(request, 'fs/nav_403.html', ctx)
        ctx['user'] = node.user
        ctx['host'] = node.host
        conn = httplib.HTTPSConnection(node.host, node.port, timeout = settings.FS_CONNECT_TIMEOUT)
        print
        conn.request('GET', '{0}ls?path={1}'.format(settings.FS_URL, urllib.quote(path.encode('utf-8'))))
        resp = conn.getresponse()
        ctx['status'] = resp.status
        body = resp.read()
        ctx['response_body'] = body
        files = json.loads(body)
        if resp.status == 200:
            # TODO: validate json format: [ ["filename1", "filetype1"], ..., ["filenameN", "filetypeN"] ]
            data = []
            if path != '/':
                data.append({
                    'name': '..',
                    'type': 'dir',
                    'url': reverse('spear-fs-nav', kwargs={'node_pk': node_pk,
                                                           'path': urllib.quote(os.path.dirname(path)[1:].encode('utf8'))}),
                    })
            for file in files:
                fname = file[0]
                ftype = file[1]
                data.append({
                    'name': fname,
                    'type': ftype,
                    'url': reverse('spear-fs-nav', kwargs={'node_pk': node_pk,
                                                           'path': urllib.quote(os.path.join(path,fname)[1:].encode('utf8'))}),
                    })
            ctx['response'] = data
            ctx['success'] = True
        else:
            ctx['success'] = False
            ctx['reason'] = resp.getheader('status', 'Executor have not provided error message')
    except socket.error as e:
        ctx['reason'] = "[" + e.__module__ + "." + e.__class__.__name__ + "] " + str(e)
    except httplib.HTTPException as e:
        ctx['reason'] = "[" + e.__module__ + "." + e.__class__.__name__ + "] " + str(e)
    except ValueError as e:
        print repr(e)
        if str(e) == 'No JSON object could be decoded':
            pass
        else:
            raise
    return render(request, 'fs/nav.html', ctx)
