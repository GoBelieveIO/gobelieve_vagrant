# -*- coding: utf-8 -*-
import time


class User(object):
    @staticmethod
    def get_user_access_token(rds, appid, uid):
        key = "users_%d_%d"%(appid, uid)
        token = rds.hget(key, "access_token")
        return token

    @staticmethod
    def load_user_access_token(rds, token):
        key = "access_token_%s"%token
        exists = rds.exists(key)
        if not exists:
            return 0, 0, ""
        uid, appid, name = rds.hget(key, "user_id", "app_id", "user_name")
        return uid, appid, name


    @staticmethod
    def save_user(rds, appid, uid, name, avatar, token):
        key = "users_%d_%d"%(appid, uid)
        obj = {
            "access_token":token,
            "name":name,
            "avatar":avatar
        }
        rds.hmset(key, obj)
        
    @staticmethod
    def save_token(rds, appid, uid, token):
        key = "access_token_%s"%token
        obj = {
            "user_id":uid,
            "app_id":appid
        }
        rds.hmset(key, obj)

    @staticmethod
    def save_user_access_token(rds, appid, uid, name, token):
        pipe = rds.pipeline()

        key = "access_token_%s"%token
        obj = {
            "user_id":uid,
            "user_name":name,
            "app_id":appid
        }
        
        pipe.hmset(key, obj)

        key = "users_%d_%d"%(appid, uid)
        obj = {
            "access_token":token,
            "name":name
        }

        pipe.hmset(key, obj)
        pipe.execute()

        return True

    @staticmethod
    def save_user_device_token(rds, appid, uid,
                               device_token, pushkit_device_token,
                               ng_device_token, xg_device_token,
                               xm_device_token, hw_device_token,
                               gcm_device_token, jp_device_token):
        now = int(time.time())
        key = "users_%d_%d"%(appid, uid)

        if device_token:
            obj = {
                "apns_device_token":device_token,
                "apns_timestamp":now
            }
            rds.hmset(key, obj)

        if pushkit_device_token:
            obj = {
                "pushkit_device_token":pushkit_device_token,
                "pushkit_timestamp":now
            }
            rds.hmset(key, obj)
            
        if ng_device_token:
            obj = {
                "ng_device_token":ng_device_token,
                "ng_timestamp":now
            }
            rds.hmset(key, obj)
            
        if xg_device_token:
            obj = {
                "xg_device_token":xg_device_token,
                "xg_timestamp":now
            }
            rds.hmset(key, obj)
            
        if xm_device_token:
            obj = {
                "xm_device_token":xm_device_token,
                "xm_timestamp":now
            }
            rds.hmset(key, obj)

        if hw_device_token:
            obj = {
                "hw_device_token":hw_device_token,
                "hw_timestamp":now
            }
            rds.hmset(key, obj)
        
        if gcm_device_token:
            obj = {
                "gcm_device_token":gcm_device_token,
                "gcm_timestamp":now
            }
            rds.hmset(key, obj)
            
        if jp_device_token:
            obj = {
                "jp_device_token":jp_device_token,
                "jp_timestamp":now
            }
            rds.hmset(key, obj)

        return True


    #重置(清空)用户已经绑定的devicetoken
    @staticmethod
    def reset_user_device_token(rds, appid, uid,
                                device_token, pushkit_device_token,
                                ng_device_token, xg_device_token, 
                                xm_device_token, hw_device_token, 
                                gcm_device_token, jp_device_token):
        key = "users_%d_%d"%(appid, uid)
        if device_token:
            t = rds.hget(key, "apns_device_token")
            if device_token != t:
                return False
            rds.hdel(key, "apns_device_token")

        if pushkit_device_token:
            t = rds.hget(key, "pushkit_device_token")
            if pushkit_device_token != t:
                return False
            rds.hdel(key, "pushkit_device_token")
            
        if ng_device_token:
            t = rds.hget(key, "ng_device_token")
            if ng_device_token != t:
                return False
            rds.hdel(key, "ng_device_token")
            
        if xg_device_token:
            t = rds.hget(key, "xg_device_token")
            if xg_device_token != t:
                return False
            rds.hdel(key, "xg_device_token")

        if xm_device_token:
            t = rds.hget(key, "xm_device_token")
            if xm_device_token != t:
                return False
            rds.hdel(key, "xm_device_token")

        if hw_device_token:
            t = rds.hget(key, "hw_device_token")
            if hw_device_token != t:
                return False
            rds.hdel(key, "hw_device_token")

        if gcm_device_token:
            t = rds.hget(key, "gcm_device_token")
            if gcm_device_token != t:
                return False
            rds.hdel(key, "gcm_device_token")
        
        if jp_device_token:
            t = rds.hget(key, "jp_device_token")
            if jp_device_token != t:
                return False
            rds.hdel(key, "jp_device_token")

        return True

    @staticmethod
    def set_user_name(rds, appid, uid, name):
        key = "users_%d_%d"%(appid, uid)
        rds.hset(key, "name", name)

    @staticmethod
    def get_user_name(rds, appid, uid):
        key = "users_%d_%d"%(appid, uid)
        return rds.hget(key, "name")

    #用户禁言设置
    @staticmethod
    def set_user_forbidden(rds, appid, uid, fb):
        key = "users_%d_%d"%(appid, uid)
        rds.hset(key, "forbidden", fb)

    #个人消息免打扰设置
    @staticmethod
    def get_user_do_not_disturb(rds, appid, uid, peer_uid):
        key = "users_%s_%s"%(appid, uid)
        q = rds.hget(key, "peer_%d"%peer_uid)
        return int(q) if q else 0

    @staticmethod
    def set_user_do_not_disturb(rds, appid, uid, peer_uid, do_not_disturb):
        key = "users_%s_%s"%(appid, uid)
        q = 1 if do_not_disturb else 0
        rds.hset(key, "peer_%d"%peer_uid, do_not_disturb)
        
        key = "users_%s_%s_peer_do_not_disturb"%(appid, uid)
        if do_not_disturb:
            rds.sadd(key, peer_uid)
        else:
            rds.srem(key, peer_uid)
    
    #群组免打扰设置
    @staticmethod
    def get_group_do_not_disturb(rds, appid, uid, group_id):
        key = "users_%s_%s"%(appid, uid)
        quiet = rds.hget(key, "group_%d"%group_id)
        q = int(quiet) if quiet else 0
        return q

    @staticmethod
    def set_group_do_not_disturb(rds, appid, uid, group_id, quiet):
        key = "users_%s_%s"%(appid, uid)
        q = 1 if quiet else 0
        rds.hset(key, "group_%d"%group_id, q)

        key = "users_%s_%s_group_do_not_disturb"%(appid, uid)
        if quiet:
            rds.sadd(key, group_id)
        else:
            rds.srem(key, group_id)

    @staticmethod
    def add_user_count(rds, appid, uid):
        key = "statistics_users_%d"%appid
        rds.pfadd(key, uid)


    @staticmethod
    def set_seller(rds, appid, uid, store_id, seller_id):
        key = "users_%s_%s"%(appid, uid)
        obj = {
            "store_id":store_id,
            "seller_id":seller_id
        }
        rds.hmset(key, obj)

    @staticmethod
    def get_seller(rds, appid, uid):
        key = "users_%s_%s"%(appid, uid)
        store_id, seller_id = rds.hmget(key, "store_id", "seller_id")
        store_id = int(store_id) if store_id else 0
        seller_id = int(seller_id) if seller_id else 0
        return store_id, seller_id
    
    @staticmethod
    def set_turn_password(rds, appid, uid, password):
        u = "%s_%s"%(appid, uid)
        key = "turn/user/%s/password"%u
        rds.set(key, password)


    @staticmethod
    def set_turn_key(rds, appid, uid, key):
        u = "%s_%s"%(appid, uid)
        k = "turn/user/%s/key"%u
        rds.set(k, key)
