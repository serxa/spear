from web.core.models import Node 
import datetime

def add_node(host, user, ssh_key):
    #TODO: check if node is already exist
    # Port=0 means that port should be determined by executor and be send back with heartbeat message
    n = Node(host=host, port=0, user=user,
             executor_path='/home/'+user+'/.spear/executor',
             status=NONE, last_heartbeat=datetime.min, ssh_key_file=ssh_key_file)
    n.save()