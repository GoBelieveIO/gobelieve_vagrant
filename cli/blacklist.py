# -*- coding: utf-8 -*-
import time
import pymysql


class Blacklist(object):
    @classmethod
    def add_blacklist(cls, db, appid, uid, friend_uid):
        now = int(time.time())
        sql = "INSERT INTO blacklist(appid, uid, friend_uid, timestamp) VALUES(%s, %s, %s, %s)"
        try:
            db.execute(sql, (appid, uid, friend_uid, now))
        except pymysql.err.IntegrityError as e:
            if e.args[0] != 1062:            
                raise

    @classmethod
    def delete_blacklist(cls, db, appid, uid, friend_uid):
        sql = "DELETE FROM blacklist WHERE uid=%s AND friend_uid=%s AND appid=%s"
        db.execute(sql, (uid, friend_uid, appid))

    @classmethod
    def get_blacklist(cls, db, appid, uid):
        sql = "SELECT friend_uid as uid FROM blacklist WHERE blacklist.uid=%s AND appid=%s"
        r = db.execute(sql, (uid, appid))
        return list(r.fetchall())

 
