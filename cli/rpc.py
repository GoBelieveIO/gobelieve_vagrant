# -*- coding: utf-8 -*-
import config
import logging
import json
import requests
from urllib.parse import urlencode
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
    except Exception as e:
        logging.warning("send group notification err:%s", e)
        return None


