# -*- coding: utf-8 -*-
import config
import requests
import logging
import json
import time
import sys
import redis
import pprint
from friend import Friend
from blacklist import Blacklist

from user import User
from rpc import send_group_notification
from mysql import Mysql
import config


rds = redis.StrictRedis(host=config.REDIS_HOST, password=config.REDIS_PASSWORD,
                        port=config.REDIS_PORT, db=config.REDIS_DB, decode_responses=True)


db = Mysql(config.MYSQL_HOST, config.MYSQL_USER, config.MYSQL_PASSWD,
           config.MYSQL_DATABASE, config.MYSQL_PORT,
           config.MYSQL_CHARSET, config.MYSQL_AUTOCOMMIT)


APPID = config.APPID

def add_friend_relation(uid, friend_uid, bidirection):
    appid = APPID
    
    Friend.add_friend_relation(db, appid, uid, friend_uid, bidirection)

    content = {
        "app_id":appid,
        "uid": uid,
        "friend_uid":friend_uid,
        "friend":1,
        "name":Friend.RELATIONSHIP_EVENT_FRIEND
    }
    Friend.publish_message(rds, content)

    if bidirection:
        content = {
            "app_id":appid,
            "uid": friend_uid,
            "friend_uid":uid,
            "friend":1,
            "name":Friend.RELATIONSHIP_EVENT_FRIEND
        }
        Friend.publish_message(rds, content)        


def add_blacklist(uid, friend_uid):
    appid = APPID

    Blacklist.add_blacklist(db, appid, uid, friend_uid)

    content = {
        "app_id":appid,
        "uid": uid,
        "friend_uid":friend_uid,
        "blacklist":1,
        "name":Friend.RELATIONSHIP_EVENT_BLACKLIST
    }
    Friend.publish_message(rds, content)    


def delete_friend_relation(uid, friend_uid, bidirection):
    appid = APPID
    Friend.delete_friend_relation(db, appid, uid, friend_uid, bidirection)


    content = {
        "app_id":appid,
        "uid": uid,
        "friend_uid":friend_uid,
        "friend":0,
        "name":Friend.RELATIONSHIP_EVENT_FRIEND
    }
    Friend.publish_message(rds, content)

    if bidirection:
        content = {
            "app_id":appid,
            "uid": friend_uid,
            "friend_uid":uid,
            "friend":0,
            "name":Friend.RELATIONSHIP_EVENT_FRIEND
        }
        Friend.publish_message(rds, content)        


def delete_blacklist(uid, friend_uid):
    appid = APPID

    Blacklist.delete_blacklist(db, appid, uid, friend_uid)

    content = {
        "app_id":appid,
        "uid": uid,
        "friend_uid":friend_uid,
        "blacklist":0,
        "name":Friend.RELATIONSHIP_EVENT_BLACKLIST
    }
    Friend.publish_message(rds, content)    

    

def get_friends(uid):
    appid = APPID
    friends = Friend.get_friends(db, appid, uid)
    return friends

def get_blacklist(uid):
    appid = APPID
    blacklist = Blacklist.get_blacklist(db, appid, uid)
    return blacklist


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "add_friend":
        uid = int(sys.argv[2])
        friend_uid = int(sys.argv[3])
        add_friend_relation(uid, friend_uid, True)
    elif cmd == "remove_friend":
        uid = int(sys.argv[2])
        friend_uid = int(sys.argv[3])        
        delete_friend_relation(uid, friend_uid, True)
    elif cmd == "add_blacklist":
        uid = int(sys.argv[2])
        friend_uid = int(sys.argv[3])        
        add_blacklist(uid, friend_uid)
    elif cmd == "remove_blacklist":
        uid = int(sys.argv[2])
        friend_uid = int(sys.argv[3])
        delete_blacklist(uid, friend_uid)
    elif cmd == "get":
        uid = int(sys.argv[2])
        friends = get_friends(uid)
        blacklist = get_blacklist(uid)
        pp = pprint.PrettyPrinter()
        pp.pprint(friends)
        pp.pprint(blacklist)        
    elif cmd == "test":
        uid = 1
        friend_uid = 2
        add_friend_relation(uid, friend_uid, True)
        add_blacklist(uid, friend_uid)
        friends = get_friends(uid)
        blacklist = get_blacklist(uid)
        pp = pprint.PrettyPrinter()
        pp.pprint(friends)
        pp.pprint(blacklist)
        delete_friend_relation(uid, friend_uid, True)
        delete_blacklist(uid, friend_uid)
