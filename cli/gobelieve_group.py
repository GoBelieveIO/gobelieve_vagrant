# -*- coding: utf-8 -*-
import config
import requests
import logging
import json
import time
import sys
import pymysql
import redis
import pprint
from group import Group
from user import User
from rpc import send_group_notification
from mysql import Mysql
import config

publish_message = Group.publish_message


rds = redis.StrictRedis(host=config.REDIS_HOST, password=config.REDIS_PASSWORD,
                        port=config.REDIS_PORT, db=config.REDIS_DB, decode_responses=True)


db = Mysql(config.MYSQL_HOST, config.MYSQL_USER, config.MYSQL_PASSWD,
           config.MYSQL_DATABASE, config.MYSQL_PORT,
           config.MYSQL_CHARSET, config.MYSQL_AUTOCOMMIT)

APPID = config.APPID

def create_group(master, name, is_super, members):
    appid = APPID
    gid = Group.create_group(db, appid, master, name, 
                             is_super, members)
    
    s = 1 if is_super else 0
    content = {
        "group_id":gid,
        "app_id":appid,
        "super":s,
        "name":Group.GROUP_EVENT_CREATE
    }    
    publish_message(rds, content)
    
    for mem in members:
        content = {
            "group_id":gid,
            "member_id":mem,
            "name":Group.GROUP_EVENT_MEMBER_ADD
        }        
        publish_message(rds, content)
    
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

    content = {"group_id":gid, "name":Group.GROUP_EVENT_DISBAND}    
    publish_message(rds, content)



def upgrade_group(gid):
    """从普通群升级为超级群"""
    appid = APPID
    group = Group.get_group(db, gid)

    members = Group.get_group_members(db, gid)

    if not group:
        raise ResponseMeta(400, "group non exists")

    Group.update_group_super(db, gid, 1)


    content = {
        "group_id":gid,
        "app_id":appid,
        "super":1,
        "name":Group.GROUP_EVENT_UPGRADE
    }    
    publish_message(rds, content)

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
        except pymysql.err.IntegrityError as e:
            if e.args[0] != 1062:            
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

        content = {
            "group_id":gid,
            "member_id":member_id,
            "name":Group.GROUP_EVENT_MEMBER_ADD
        }        
        publish_message(rds, content)



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

    content = {
        "group_id":gid,
        "member_id":memberid,
        "name":Group.GROUP_EVENT_MEMBER_REMOVE
    }    
    publish_message(rds, content)
    


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
        print("new group id:", gid)
        
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

    elif cmd == "test":
        master = 1
        name = "test"
        is_super = 0
        members = [1, 2, 3, 4]
        gid = create_group(master, name, is_super, members)
        print("new group id:", gid)
      

        add_group_member(gid, [5, 6])
        remove_group_member(gid, 6)
        
        upgrade_group(gid)

        groups = get_groups(master)
        
        pp = pprint.PrettyPrinter()
        pp.pprint(groups)

        delete_group(gid)
