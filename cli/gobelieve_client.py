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
import random
from gobelieve_auth import grant_auth_token
from gobelieve_group import create_group, delete_group
from protocol import *


HOST = "127.0.0.1"

def login(uid):
    return grant_auth_token(uid, "")


task = 0

def connect_server(uid, port):
    token = login(uid)
    if not token:
        return None, 0
    seq = 0
    address = (HOST, port)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
    sock.connect(address)
    auth = AuthenticationToken()
    auth.token = token
    seq = seq + 1
    send_message(MSG_AUTH_TOKEN, seq, auth, sock)
    cmd, _, msg = recv_message(sock)
    if cmd != MSG_AUTH_STATUS or msg != 0:
        return None, 0
    return sock, seq



count = 1

def recv_group_client(uid, group_id, port, handler):
    recv_client_(uid, port, handler, group_id)

def recv_client(uid, port, handler):
    recv_client_(uid, port, handler, None)

def recv_client_(uid, port, handler, group_id):
    global task
    sock, seq =  connect_server(uid, port)

    group_sync_keys = {}
    sync_key = 0

    seq += 1
    send_message(MSG_SYNC, seq, sync_key, sock)
    if group_id:
        group_sync_keys[group_id] = 0
        seq += 1
        send_message(MSG_SYNC_GROUP, seq, (group_id, sync_key), sock)
    quit = False
    begin = False
    while True:
        cmd, s, msg = recv_message(sock)
        print "cmd:", cmd, "msg:", msg
        if cmd == MSG_SYNC_BEGIN:
            begin = True
        elif cmd == MSG_SYNC_END:
            begin = False
            new_sync_key = msg
            if new_sync_key > sync_key:
                sync_key = new_sync_key
                seq += 1
                send_message(MSG_SYNC_KEY, seq, sync_key, sock)
            if quit:
                break
        elif cmd == MSG_SYNC_NOTIFY:
            new_sync_key = msg
            if new_sync_key > sync_key:
                seq += 1
                send_message(MSG_SYNC, seq, sync_key, sock)
        elif cmd == MSG_SYNC_GROUP_NOTIFY:
            group_id, new_sync_key = msg
            skey = group_sync_keys.get(group_id, 0)
            if new_sync_key > skey:
                seq += 1
                send_message(MSG_SYNC_GROUP, seq, (group_id, skey), sock)
        elif cmd == MSG_SYNC_GROUP_BEGIN:
            begin = True
        elif cmd == MSG_SYNC_GROUP_END:
            begin = False
            group_id, new_sync_key = msg
            skey = group_sync_keys.get(group_id, 0)
            if new_sync_key > skey:
                group_sync_keys[group_id] = new_sync_key
                skey = group_sync_keys.get(group_id, 0)
                seq += 1
                send_message(MSG_GROUP_SYNC_KEY, seq, (group_id, skey), sock)
            if quit:
                break

        elif handler(cmd, s, msg):
            quit = True
            if not begin:
                break


    sock.close()
    task += 1
    
def recv_group_client(uid, group_id, port, handler):
    recv_client_(uid, port, handler, group_id)
    
def recv_message_client(uid, port=23000):
    def handle_message(cmd, s, msg):
        if cmd == MSG_IM:
            return True
        else:
            return False

    recv_client(uid, port, handle_message)
    print "recv message success"

def recv_group_message_client(uid, port=23000, group_id = 0):
    def handle_message(cmd, s, msg):
        if cmd == MSG_GROUP_IM:
            return True
        elif cmd == MSG_IM:
            return False
        else:
            return False
    recv_group_client(uid, group_id, port, handle_message)
    print "recv group message success"

def send_client(uid, receiver, msg_type):
    global task
    sock, seq =  connect_server(uid, 23000)
    im = IMMessage()
    im.sender = uid
    im.receiver = receiver
    if msg_type == MSG_IM:
        im.content = "test im %s" % random.randint(0, 2<<32)
    else:
        im.content = "test group im %s" % random.randint(0, 2<<32)
    seq += 1
    send_message(msg_type, seq, im, sock)
    msg_seq = seq
    while True:
        cmd, s, msg = recv_message(sock)
        if cmd == MSG_ACK and msg == msg_seq:
            break
        elif cmd == MSG_GROUP_NOTIFICATION:
            print "send ack..."
            seq += 1
            send_message(MSG_ACK, seq, s, sock)
        else:
            pass
        
    sock.close()    
    task += 1
    print "send success"

    


def TestSendAndRecv():
    global task
    task = 0
 
    t3 = threading.Thread(target=recv_message_client, args=(13800000000,))
    t3.setDaemon(True)
    t3.start()
    
    time.sleep(1)
    
    t2 = threading.Thread(target=send_client, args=(13800000001, 13800000000, MSG_IM))
    t2.setDaemon(True)
    t2.start()
    
    while task < 2:
        time.sleep(1)
    print "test peer message completed"


        
def TestGroupMessage():
    global task
    is_super = False
    task = 0

    t3 = threading.Thread(target=recv_group_message_client, args=(13800000001,))
    t3.setDaemon(True)
    t3.start()

    time.sleep(1)

    group_id = create_group(13800000000, "test", is_super, [13800000000,13800000001])
    
    print "group id:", group_id
    time.sleep(1)

    t2 = threading.Thread(target=send_client, args=(13800000000, group_id, MSG_GROUP_IM))
    t2.setDaemon(True)
    t2.start()

    while task < 2:
        time.sleep(1)

    delete_group(group_id)
    print "test group message completed"

    
def main():
    TestSendAndRecv()
    TestGroupMessage()
   


if __name__ == "__main__":
    main()

