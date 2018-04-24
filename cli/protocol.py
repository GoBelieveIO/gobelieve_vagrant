# -*- coding: utf-8 -*-
import struct
import socket
import threading
import time
import requests
import json
import uuid
import base64
import md5
import sys

MSG_HEARTBEAT = 1
#MSG_AUTH = 2
MSG_AUTH_STATUS = 3
MSG_IM = 4
MSG_ACK = 5
MSG_RST = 6
MSG_GROUP_NOTIFICATION = 7
MSG_GROUP_IM = 8
MSG_PEER_ACK = 9
MSG_INPUTING = 10
MSG_SUBSCRIBE_ONLINE_STATE = 11
MSG_ONLINE_STATE = 12
MSG_PING = 13
MSG_PONG = 14
MSG_AUTH_TOKEN = 15
MSG_LOGIN_POINT = 16
MSG_RT = 17
MSG_ENTER_ROOM = 18
MSG_LEAVE_ROOM = 19
MSG_ROOM_IM = 20
MSG_SYSTEM = 21
MSG_UNREAD_COUNT = 22
MSG_CUSTOMER_SERVICE_ = 23

MSG_SYNC = 26
MSG_SYNC_BEGIN = 27
MSG_SYNC_END = 28
MSG_SYNC_NOTIFY = 29

MSG_SYNC_GROUP = 30
MSG_SYNC_GROUP_BEGIN = 31
MSG_SYNC_GROUP_END = 32
MSG_SYNC_GROUP_NOTIFY = 33

MSG_SYNC_KEY  = 34
MSG_GROUP_SYNC_KEY = 35

MSG_NOTIFICATION = 36



PLATFORM_IOS = 1
PLATFORM_ANDROID = 2

PROTOCOL_VERSION = 1


device_id = "f9d2a7c2-701a-11e5-9c3e-34363bd464b2"

class AuthenticationToken:
    def __init__(self):
        self.token = ""
        self.platform_id = PLATFORM_ANDROID
        self.device_id = device_id

class IMMessage:
    def __init__(self):
        self.sender = 0
        self.receiver = 0
        self.timestamp = 0
        self.msgid = 0
        self.content = ""

    def __str__(self):
        return str((self.sender, self.receiver, self.timestamp, self.content))


#RoomMessage
class RTMessage:
    def __init__(self):
        self.sender = 0
        self.receiver = 0
        self.content = ""
    def __str__(self):
        return str((self.sender, self.receiver, self.content))


def send_message(cmd, seq, msg, sock):
    if cmd == MSG_AUTH_TOKEN:
        b = struct.pack("!BB", msg.platform_id, len(msg.token)) + msg.token + struct.pack("!B", len(msg.device_id)) + msg.device_id
        length = len(b)
        h = struct.pack("!iibbbb", length, seq, cmd, PROTOCOL_VERSION, 0, 0)
        sock.sendall(h+b)
    elif cmd == MSG_IM or cmd == MSG_GROUP_IM:
        length = 24 + len(msg.content)
        h = struct.pack("!iibbbb", length, seq, cmd, PROTOCOL_VERSION, 0, 0)
        b = struct.pack("!qqii", msg.sender, msg.receiver, msg.timestamp, msg.msgid)
        sock.sendall(h+b+msg.content)
    elif cmd == MSG_RT or cmd == MSG_ROOM_IM:
        length = 16 + len(msg.content)
        h = struct.pack("!iibbbb", length, seq, cmd, PROTOCOL_VERSION, 0, 0)
        b = struct.pack("!qq", msg.sender, msg.receiver)
        sock.sendall(h+b+msg.content)
    elif cmd == MSG_ACK:
        h = struct.pack("!iibbbb", 4, seq, cmd, PROTOCOL_VERSION, 0, 0)
        b = struct.pack("!i", msg)
        sock.sendall(h + b)
    elif cmd == MSG_INPUTING:
        sender, receiver = msg
        h = struct.pack("!iibbbb", 16, seq, cmd, PROTOCOL_VERSION, 0, 0)
        b = struct.pack("!qq", sender, receiver)
        sock.sendall(h + b)
    elif cmd == MSG_PING:
        h = struct.pack("!iibbbb", 0, seq, cmd, PROTOCOL_VERSION, 0, 0)
        sock.sendall(h)
    elif cmd == MSG_ENTER_ROOM or cmd == MSG_LEAVE_ROOM:
        h = struct.pack("!iibbbb", 8, seq, cmd, PROTOCOL_VERSION, 0, 0)
        b = struct.pack("!q", msg)
        sock.sendall(h+b)
    elif cmd == MSG_SYNC or cmd == MSG_SYNC_KEY:
        h = struct.pack("!iibbbb", 8, seq, cmd, PROTOCOL_VERSION, 0, 0)
        b = struct.pack("!q", msg)
        sock.sendall(h+b)
    elif cmd == MSG_SYNC_GROUP or cmd == MSG_GROUP_SYNC_KEY:
        group_id, sync_key = msg
        h = struct.pack("!iibbbb", 16, seq, cmd, PROTOCOL_VERSION, 0, 0)
        b = struct.pack("!qq", group_id, sync_key)
        sock.sendall(h+b)
    else:
        print "eeeeee"

def recv_message(sock):
    buf = sock.recv(12)
    if len(buf) != 12:
        return 0, 0, None
    length, seq, cmd = struct.unpack("!iib", buf[:9])

    if length == 0:
        return cmd, seq, None

    content = sock.recv(length)
    if len(content) != length:
        return 0, 0, None

    if cmd == MSG_AUTH_STATUS:
        status, = struct.unpack("!i", content)
        return cmd, seq, status
    elif cmd == MSG_LOGIN_POINT:
        up_timestamp, platform_id = struct.unpack("!ib", content[:5])
        device_id = content[5:]
        return cmd, seq, (up_timestamp, platform_id, device_id)
    elif cmd == MSG_IM or cmd == MSG_GROUP_IM:
        im = IMMessage()
        im.sender, im.receiver, im.timestamp, _ = struct.unpack("!qqii", content[:24])
        im.content = content[24:]
        return cmd, seq, im
    elif cmd == MSG_RT or cmd == MSG_ROOM_IM:
        rt = RTMessage()
        rt.sender, rt.receiver, = struct.unpack("!qq", content[:16])
        rt.content = content[16:]
        return cmd, seq, rt
    elif cmd == MSG_ACK:
        ack, = struct.unpack("!i", content)
        return cmd, seq, ack
    elif cmd == MSG_SYSTEM:
        return cmd, seq, content
    elif cmd == MSG_NOTIFICATION:
        return cmd, seq, content
    elif cmd == MSG_INPUTING:
        sender, receiver = struct.unpack("!qq", content)
        return cmd, seq, (sender, receiver)
    elif cmd == MSG_PONG:
        return cmd, seq, None
    elif cmd == MSG_SYNC_BEGIN or \
         cmd == MSG_SYNC_END or \
         cmd == MSG_SYNC_NOTIFY:
        sync_key, = struct.unpack("!q", content)
        return cmd, seq, sync_key
    elif cmd == MSG_SYNC_GROUP_BEGIN or \
         cmd == MSG_SYNC_GROUP_END or \
         cmd == MSG_SYNC_GROUP_NOTIFY:
        group_id, sync_key = struct.unpack("!qq", content)
        return cmd, seq, (group_id, sync_key)
    elif cmd == MSG_GROUP_NOTIFICATION:
        return cmd, seq, content
    else:
        print "unknow cmd:", cmd
        return cmd, seq, content
