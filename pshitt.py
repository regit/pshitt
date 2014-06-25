#!/usr/bin/env python

# Copyright (C) 2003-2007  Robey Pointer <robeypointer@gmail.com>
# Copyright (C) 2014 Eric Leblond <eric@regit.org>
#
# Software base on demo_server.py example provided in paramiko
#
# Paramiko is free software; you can redistribute it and/or modify it under the
# terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; either version 2.1 of the License, or (at your option)
# any later version.
#
# Paramiko is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Paramiko; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA.

import base64
from binascii import hexlify
import os
import socket
import sys
import threading
import traceback
import json
from datetime import datetime
import threading


import paramiko
from paramiko.py3compat import b, u, decodebytes

logfile = open('passwords.log', 'a')

# setup logging
paramiko.util.log_to_file('demo_server.log')

host_key = paramiko.RSAKey(filename='test_rsa.key')
#host_key = paramiko.DSSKey(filename='test_dss.key')

addr = None

class Server (paramiko.ServerInterface):
    # 'data' is the output of base64.encodestring(str(key))
    # (using the "user_rsa_key" files)
    data = (b'AAAAB3NzaC1yc2EAAAABIwAAAIEAyO4it3fHlmGZWJaGrfeHOVY7RWO3P9M7hp'
            b'fAu7jJ2d7eothvfeuoRFtJwhUmZDluRdFyhFY/hFAh76PJKGAusIqIQKlkJxMC'
            b'KDqIexkgHAfID/6mqvmnSJf0b5W8v5h2pI/stOSwTQ+pxVhwJ9ctYDhRSlF0iT'
            b'UWT10hcuO4Ks8=')
    good_pub_key = paramiko.RSAKey(data=decodebytes(data))

    def __init__(self):
        self.event = threading.Event()

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_password(self, username, password):
        data = {}
        data['username'] = username
        data['password'] = password
        data['src_ip'] = self.addr
        data['src_port'] = self.port
        data['timestamp'] = datetime.isoformat(datetime.now())
        logfile.write(json.dumps(data) + '\n')
        logfile.flush()
        return paramiko.AUTH_FAILED

    def check_auth_publickey(self, username, key):
        print('Auth attempt with key: ' + u(hexlify(key.get_fingerprint())))
        return paramiko.AUTH_FAILED

    def get_allowed_auths(self, username):
        return 'password,publickey'

    def check_channel_shell_request(self, channel):
        self.event.set()
        return False

    def check_channel_pty_request(self, channel, term, width, height, pixelwidth,
                                  pixelheight, modes):
        return False

    def set_ip_param(self, addr):
        self.addr = addr[0]
        self.port = addr[1]

def handle_client(client, addr):
    try:
        t = paramiko.Transport(client)
        try:
            t.load_server_moduli()
        except:
            raise
        t.add_server_key(host_key)
        server = Server()
        server.set_ip_param(addr)
        try:
            t.start_server(server=server)
        except paramiko.SSHException:
            print('*** SSH negotiation failed.')
            return

        # wait for auth
        chan = t.accept(20)
    except:
        print('***SSH connect failure')
        return

# now connect
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', 2200))
except Exception as e:
    traceback.print_exc()
    sys.exit(1)

try:
    sock.listen(100)
except Exception as e:
    traceback.print_exc()
    sys.exit(1)

while True:
    client, addr = sock.accept()
    t = threading.Thread(target=handle_client, args=(client, addr,))
    t.setDaemon(True)
    t.start()
