# -*- coding: utf-8 -*-
import logging
import redis

class Group(object):
    GROUP_EVENT_CREATE = "group_create"
    GROUP_EVENT_DISBAND = "group_disband"
    GROUP_EVENT_UPGRADE = "group_upgrade"
    GROUP_EVENT_MEMBER_ADD = "group_member_add"
    GROUP_EVENT_MEMBER_REMOVE = "group_member_remove"
    GROUP_EVENT_MEMBER_MUTE = "group_member_mute"

    
    #外部指定groupid
    @staticmethod
    def create_group_ext(db, group_id, appid, master, name, is_super, members):
        db.begin()
        sql = "INSERT INTO `group`(id, appid, master, name, super) VALUES(%s, %s, %s, %s, %s)"

        s = 1 if is_super else 0
        r = db.execute(sql, (group_id, appid, master, name, s))

        for m in members:
            sql = "INSERT INTO group_member(group_id, uid) VALUES(%s, %s)"
            db.execute(sql, (group_id, m))

        db.commit()
        return group_id

    #使用自增的groupid
    @staticmethod
    def create_group(db, appid, master, name, is_super, members):
        db.begin()
        sql = "INSERT INTO `group`(appid, master, name, super) VALUES(%s, %s, %s, %s)"

        s = 1 if is_super else 0
        r = db.execute(sql, (appid, master, name, s))
        group_id = r.lastrowid
        
        for m in members:
            sql = "INSERT INTO group_member(group_id, uid) VALUES(%s, %s)"
            db.execute(sql, (group_id, m))
        
        db.commit()
        return group_id

    @staticmethod
    def update_group_name(db, group_id, name):
        sql = "UPDATE `group` SET name=%s WHERE id=%s"
        r = db.execute(sql, (name, group_id))
        logging.debug("update group name rows:%s", r.rowcount)

    @staticmethod
    def update_group_notice(db, group_id, notice):
        sql = "UPDATE `group` SET notice=%s WHERE id=%s"
        r = db.execute(sql, (notice, group_id))
        logging.debug("update group notice rows:%s", r.rowcount)
        
    @staticmethod
    def update_group_super(db, group_id, is_super):
        sql = "UPDATE `group` SET super=%s WHERE id=%s"
        s = 1 if is_super else 0
        r = db.execute(sql, (s, group_id))
        logging.debug("update group super:%s", r.rowcount)
        
    @staticmethod
    def disband_group(db, group_id):
        db.begin()
        sql = "DELETE FROM `group` WHERE id=%s"
        r = db.execute(sql, group_id)
        logging.debug("rows:%s", r.rowcount)

        sql = "DELETE FROM group_member WHERE group_id=%s"
        r = db.execute(sql, group_id)
        logging.debug("delete group rows:%s", r.rowcount)
        db.commit()

    @staticmethod
    def add_group_member(db, group_id, member_id):
        sql = "INSERT INTO group_member(group_id, uid) VALUES(%s, %s)"
        r = db.execute(sql, (group_id, member_id))
        logging.debug("insert rows:%s", r.rowcount)

    @staticmethod
    def delete_group_member(db, group_id, member_id):
        sql = "DELETE FROM group_member WHERE group_id=%s AND uid=%s"
        r = db.execute(sql, (group_id, member_id))
        logging.debug("delete group member rows:%s", r.rowcount)

    @staticmethod
    def get_group_members(db, group_id):
        sql = "SELECT uid, nickname FROM group_member WHERE group_id=%s"
        r = db.execute(sql, group_id)
        return list(r.fetchall())

    @staticmethod
    def update_nickname(db, group_id, member_id, nickname):
        sql = "UPDATE `group_member` SET nickname=%s WHERE group_id=%s AND uid=%s"
        r = db.execute(sql, (nickname, group_id, member_id))
        logging.debug("update nickname rows:%s", r.rowcount)        

    @staticmethod
    def get_group_master(db, group_id):
        sql = "SELECT master FROM `group` WHERE id=%s"
        cursor = db.execute(sql, group_id)
        r = cursor.fetchone()
        master = r["master"]
        return master

    @staticmethod
    def get_group(db, group_id):
        sql = "SELECT id, appid, master, super, name, COALESCE(notice, '') as notice FROM `group` WHERE id=%s"
        cursor = db.execute(sql, group_id)
        r = cursor.fetchone()
        return r
        

    #获取用户所在的所有群
    @staticmethod
    def get_groups(db, appid, uid):
        sql = "SELECT g.id, g.appid, g.master, g.super, g.name, COALESCE(g.notice, '') as notice FROM `group_member`, `group` as g WHERE group_member.uid=%s AND group_member.group_id=g.id AND g.appid=%s"
        cursor = db.execute(sql, (uid, appid))
        return list(cursor.fetchall())


    
    #groups_actions_id 每个操作的序号，自增
    #groups_actions 记录之前的action ID 和当前的action ID 格式："prev_id:id"
    @staticmethod
    def publish_message(rds, msg):
        with rds.pipeline() as pipe:
            while True:
                try:
                    pipe.watch("groups_actions_id")
                    pipe.watch("groups_actions")
                    action_id = pipe.get("groups_actions_id")
                    action_id = int(action_id) if action_id else 0
                    action_id = action_id + 1
                    
                    group_actions = pipe.get("groups_actions")
                    prev_id = 0
                    if group_actions:
                        _, prev_id = group_actions.split(":")
                    
                    pipe.multi()
                    
                    pipe.set("groups_actions_id", action_id)
                    
                    group_actions = "%s:%s"%(prev_id, action_id)
                    pipe.set("groups_actions", group_actions)
     
                    m = msg.copy()
                    m["previous_action_id"] = prev_id
                    m["action_id"] = action_id
                    pipe.xadd("group_manager_stream", m, maxlen=100000)
                    
                    pipe.execute()
                    logging.info("xadd group event:%s to stream", m)
                    break
                except redis.WatchError as e:
                    logging.info("watch err:%s", e)
                    

        
   
