# -*- coding: utf-8 -*-
import config
import requests
from urllib import urlencode
import logging
import json
import time
import sys
import umysql
import redis
import pprint
from group import Group
from user import User
from rpc import send_group_notification
from mysql import Mysql
import config

publish_message = Group.publish_message

rds = redis.StrictRedis(host=config.REDIS_HOST, port=config.REDIS_PORT,
                        password=config.REDIS_PASSWORD, db=config.REDIS_DB)

db = Mysql(*config.MYSQL)
APPID = config.APPID

def create_group(master, name, is_super, members):
    appid = APPID
    gid = Group.create_group(db, appid, master, name, 
                             is_super, members)
    
    s = 1 if is_super else 0
    content = "%d,%d,%d"%(gid, appid, s)
    publish_message(rds, "group_create", content)
    
    for mem in members:
        content = "%d,%d"%(gid, mem)
        publish_message(rds, "group_member_add", content)
    
    v = {
        "group_id":gid, 
        "master":master, 
        "name":name, 
        "members":members,
        "timestamp":int(time.time())
    }
    op = {"create":v}
    send_group_notification(appid, gid, op, members)
    
    return gid



def delete_group(gid):
    appid = APPID
    Group.disband_group(db, gid)

    v = {
        "group_id":gid,
        "timestamp":int(time.time())
    }
    op = {"disband":v}
    send_group_notification(appid, gid, op, None)

    content = "%d"%gid
    publish_message(rds, "group_disband", content)




def upgrade_group(gid):
    """从普通群升级为超级群"""
    appid = APPID
    group = Group.get_group(db, gid)

    members = Group.get_group_members(db, gid)

    if not group:
        raise ResponseMeta(400, "group non exists")

    Group.update_group_super(db, gid, 1)

    content = "%d,%d,%d"%(gid, appid, 1)
    publish_message(rds, "group_upgrade", content)

    v = {
        "group_id":gid,
        "timestamp":int(time.time()),
        "super":1
    }
    op = {"upgrade":v}
    send_group_notification(appid, gid, op, None)


def update_group(gid):
    """更新群组名称"""
    appid = request.appid
    obj = json.loads(request.data)
    name = obj["name"]
    Group.update_group_name(db, gid, name)

    v = {
        "group_id":gid,
        "timestamp":int(time.time()),
        "name":name
    }
    op = {"update_name":v}
    send_group_notification(appid, gid, op, None)
    
def add_group_member(gid, members):
    appid = APPID
    if len(members) == 0:
        return

    db.begin()
    for member_id in members:
        try:
            Group.add_group_member(db, gid, member_id)
        except umysql.SQLError, e:
            #1062 duplicate member
            if e[0] != 1062:
                raise

    db.commit()

    for member_id in members:
        v = {
            "group_id":gid,
            "member_id":member_id,
            "timestamp":int(time.time())
        }
        op = {"add_member":v}
        send_group_notification(appid, gid, op, [member_id])
         
        content = "%d,%d"%(gid, member_id)
        publish_message(rds, "group_member_add", content)



def remove_group_member(gid, memberid):
    appid = APPID
    Group.delete_group_member(db, gid, memberid)
         
    v = {
        "group_id":gid,
        "member_id":memberid,
        "timestamp":int(time.time())
    }
    op = {"quit_group":v}
    send_group_notification(appid, gid, op, [memberid])
     
    content = "%d,%d"%(gid,memberid)
    publish_message(rds, "group_member_remove", content)
    


def get_groups(uid):
    """获取个人的群组列表"""
    appid = APPID
    groups = Group.get_groups(db, appid, uid)
    return groups

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "create":
        master = int(sys.argv[2])
        name = sys.argv[3]
        is_super = int(sys.argv[4])
        members = []
        for m in sys.argv[5:]:
            members.append(int(m))

        gid = create_group(master, name, is_super, members)
        print gid
        
    elif cmd == "delete":
        gid = int(sys.argv[2])
        delete_group(gid)
        
    elif cmd == "upgrade":
        gid = int(sys.argv[2])
        upgrade_group(gid)
        
    elif cmd == "add_member":
        gid = int(sys.argv[2])
        members = []        
        for m in sys.argv[3:]:
            members.append(int(m))

        add_group_member(gid, members)

    elif cmd == "remove_member":
        gid = int(sys.argv[2])
        for m in sys.argv[3:]:
            remove_group_member(gid, int(m))
            
    elif cmd == "get":
        uid = int(sys.argv[2])
        groups = get_groups(uid)        
        pp = pprint.PrettyPrinter()
        pp.pprint(groups)
