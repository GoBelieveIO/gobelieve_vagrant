# -*- coding: utf-8 -*-
import config
import logging
import json
import requests
from urllib import urlencode
import config

im_url=config.IM_RPC_URL


def post_message(appid, sender, receiver, cls, content):
    params = {
        "appid":appid,
        "class":cls,
        "sender":sender
    }

    req_obj = {
        "receiver":receiver,
        "content":content,
    }

    url = im_url + "/post_im_message?" + urlencode(params)
    logging.debug("url:%s", url)
    headers = {"Content-Type":"application/json"}
    res = requests.post(url, data=json.dumps(req_obj), headers=headers)
    return res
    


def send_group_notification_s(appid, gid, notification, members):
    url = im_url + "/post_group_notification"

    obj = {
        "appid": appid,
        "group_id": gid,
        "notification":notification
    }
    if members:
        obj["members"] = members

    headers = {"Content-Type":"application/json"}

    data = json.dumps(obj)
    resp = requests.post(url, data=data, headers=headers)
    if resp.status_code != 200:
        logging.warning("send group notification error:%s", resp.content)
    else:
        logging.debug("send group notification success:%s", data)
    return resp

def send_group_notification(appid, gid, op, members):
    try:
        return send_group_notification_s(appid, gid, json.dumps(op), members)
    except Exception, e:
        logging.warning("send group notification err:%s", e)
        return None


def init_message_queue(appid, uid, platform_id, device_id):
    obj = {
        "appid":appid,
        "uid":uid,
        "device_id":device_id,
        "platform_id":platform_id
    }

    url = im_url + "/init_message_queue"
    logging.debug("url:%s", url)
    headers = {"Content-Type":"application/json"}
    res = requests.post(url, data=json.dumps(obj), headers=headers)
    return res.status_code == 200

def get_offline_count(appid, uid, platform_id, device_id):
    obj = {
        "appid":appid,
        "uid":uid,
        "device_id":device_id,
        "platform_id":platform_id
    }

    url = im_url + "/get_offline_count"
    logging.debug("url:%s", url)
    headers = {"Content-Type":"application/json"}
    res = requests.get(url, params=obj, headers=headers)
    if res.status_code != 200:
        return 0
    else:
        r = json.loads(res.content)
        return r["data"]["count"]
    
def dequeue_message(appid, uid, msgid):
    obj = {
        "appid":appid,
        "uid":uid,
        "msgid":msgid
    }

    url = im_url + "/dequeue_message"
    headers = {"Content-Type":"application/json"}
    res = requests.post(url, data=json.dumps(obj), headers=headers)
    print res.content
    return res.status_code == 200
    
