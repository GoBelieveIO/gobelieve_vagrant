# -*- coding: utf-8 -*-
import time
import pymysql
import redis
import logging

class Friend(object):
    RELATIONSHIP_EVENT_FRIEND = "friend"
    RELATIONSHIP_EVENT_BLACKLIST = "blacklist"

    @classmethod
    def get_friends(cls, db, appid, uid):
        sql = "SELECT friend_uid as uid FROM friend " \
              "WHERE friend.uid=%s and appid=%s"
        r = db.execute(sql, (uid, appid))
        return list(r.fetchall())

    
    @classmethod
    def add_friend_relation(cls, db, appid, uid, friend_uid, bidirection=True):
        now = int(time.time())
        db.begin()
        sql = "INSERT INTO friend(appid, uid, friend_uid, timestamp) VALUES(%s, %s, %s, %s)"
        try:
            db.execute(sql, (appid, uid, friend_uid, now))
        except pymysql.err.IntegrityError as e:
            if e.args[0] != 1062:            
                raise

        if bidirection:
            try:
                db.execute(sql, (appid, friend_uid, uid, now))
            except pymysql.err.IntegrityError as e:
                if e.args[0] != 1062:
                    raise                     
        db.commit()

    @classmethod
    def delete_friend_relation(cls, db, appid, uid, friend_uid, bidirection=True):
        db.begin()
        sql = "DELETE FROM friend WHERE uid=%s AND friend_uid=%s AND appid=%s"
        db.execute(sql, (uid, friend_uid, appid))
        if bidirection:
            db.execute(sql, (friend_uid, uid, appid))
        db.commit()

    @classmethod
    def get_friend_relation(cls, db, appid, uid, friend_uid):
        """return the relation with friend_uid"""
        sql = "SELECT uid, friend_uid FROM friend WHERE uid=%s AND friend_uid=%s AND appid=%s"
        r = db.execute(sql, (uid, friend_uid, appid))
        return bool(r.fetchone())


    # friends_actions_id 每个操作的序号，自增
    # friends_actions 记录之前的action ID 和当前的action ID 格式："prev_id:id"
    @classmethod
    def publish_message(cls, rds, msg):
        with rds.pipeline() as pipe:
            while True:
                try:
                    pipe.watch("friends_actions_id")
                    pipe.watch("friends_actions")
                    action_id = pipe.get("friends_actions_id")
                    action_id = int(action_id) if action_id else 0
                    action_id = action_id + 1

                    friend_actions = pipe.get("friends_actions")
                    prev_id = 0
                    if friend_actions:
                        _, prev_id = friend_actions.split(":")

                    pipe.multi()

                    pipe.set("friends_actions_id", action_id)

                    friend_actions = "%s:%s" % (prev_id, action_id)
                    pipe.set("friends_actions", friend_actions)

                    m = msg.copy()
                    m["previous_action_id"] = prev_id
                    m["action_id"] = action_id                    
                    pipe.xadd("relationship_stream", m, maxlen=1000)
                    
                    pipe.execute()
                    logging.info("xadd relationsihp event:%s to stream", m)
                    break
                except redis.WatchError as e:
                    logging.info("watch err:%s", e)

