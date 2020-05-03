#!/usr/bin/env python
"""
Copyright(C) 2014-2020, Eric Leblond
Written by Eric Leblond <eric@regit.org>


Software based on demo_server.py example provided in paramiko
Copyright (C) 2003-2007  Robey Pointer <robeypointer@gmail.com>

pshitt is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

pshitt is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with pshitt.  If not, see <http://www.gnu.org/licenses/>.
"""

from binascii import hexlify
from datetime import datetime
import argparse
import json
import logging
import os
import socket
import sys
import threading
import traceback
# third party dependencies
import paramiko
import daemon


class Server(paramiko.ServerInterface):
    def __init__(self):
        self.event = threading.Event()
        self.count = 1

    def set_transport(self, transport):
        self.transport = transport

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_password(self, username, password):
        data = {}
        data['username'] = username
        data['password'] = password
        if self.addr.startswith('::ffff:'):
            data['src_ip'] = self.addr.replace('::ffff:', '')
        else:
            data['src_ip'] = self.addr
        data['src_port'] = self.port
        data['timestamp'] = datetime.isoformat(datetime.utcnow())
        try:
            rversion = self.transport.remote_version.split('-', 2)[2]
            data['software_version'] = rversion
        except Exception:
            data['software_version'] = self.transport.remote_version
            pass
        data['cipher'] = self.transport.remote_cipher
        data['mac'] = self.transport.remote_mac
        data['try'] = self.count
        self.count += 1
        logging.debug("%s:%d tried username '%s' with '%s'" %
                      (self.addr, self.port, username, password))
        self.logfile.write(json.dumps(data) + '\n')
        self.logfile.flush()
        return paramiko.AUTH_FAILED

    def check_auth_publickey(self, username, key):
        logging.debug(b'Auth attempt with key: ' +
                      hexlify(key.get_fingerprint()))
        return paramiko.AUTH_FAILED

    def get_allowed_auths(self, username):
        return 'password,publickey'

    def check_channel_shell_request(self, channel):
        self.event.set()
        return False

    def check_channel_pty_request(self, channel, term, width, height,
                                  pixelwidth, pixelheight, modes):
        return False

    def set_ip_param(self, addr):
        self.addr = addr[0]
        self.port = addr[1]

    def set_logfile(self, logfile):
        self.logfile = logfile


class Pshitt(object):
    def __init__(self, args):
        self.args = args
        self.logfile = open(args.output, 'a')
        self._setup_logging()
        self._setup_paramiko()

    def _setup_logging(self):
        if self.args.verbose >= 3:
            self.loglevel = logging.DEBUG
        elif self.args.verbose >= 2:
            self.loglevel = logging.INFO
        elif self.args.verbose >= 1:
            self.loglevel = logging.WARNING
        else:
            self.loglevel = logging.ERROR
        if self.args.log:
            self.logging = logging.basicConfig(
                filename=self.args.log,
                format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                level=self.loglevel)
        else:
            self.logging = logging.basicConfig(level=self.loglevel)

    def handle_client(self, client, addr):
        try:
            t = paramiko.Transport(client)
            t.local_version = self.args.version
            try:
                t.load_server_moduli()
            except Exception:
                raise
            t.add_server_key(self.host_key)
            server = Server()
            server.set_ip_param(addr)
            server.set_logfile(self.logfile)
            try:
                t.start_server(server=server)
            except paramiko.SSHException:
                logging.info('SSH negotiation failed.')
                return
            server.set_transport(t)
            # wait for auth
            chan = t.accept(20)
        except Exception:
            logging.info('SSH connect failure')
            return

    def _setup_paramiko(self):
        paramiko.util.log_to_file(self.args.log, level=self.loglevel)
        self.host_key = paramiko.RSAKey(filename=self.args.key)

    def run(self, args):
        logging.info('Starting SSH server')
        # now connect
        try:
            sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
            sock.bind(('', args.port))
        except Exception:
            traceback.print_exc()
            sys.exit(1)
        try:
            sock.listen(100)
        except Exception:
            traceback.print_exc()
            sys.exit(1)

        while True:
            client, addr = sock.accept()
            if len(threading.enumerate()) <= args.threads * 2:
                logging.debug(
                    'Accepted new client: %s:%d' % (addr[0], addr[1]))
                t = threading.Thread(
                    target=self.handle_client,
                    args=(client, addr))
                t.setDaemon(True)
                t.start()
            else:
                logging.info('Too many clients')
                client.close()


def main():
    parser = argparse.ArgumentParser(
        description='Passwords of SSH Intruders Transferred to Text')
    parser.add_argument(
        '-o',
        '--output',
        default='passwords.log',
        help='File to export collected data')
    parser.add_argument(
        '-k', '--key', default='test_rsa.key', help='Host RSA key')
    parser.add_argument(
        '-l', '--log', default='pshitt.log', help='File to log info and debug')
    parser.add_argument(
        '-p', '--port', type=int, default=2200, help='TCP port to listen to')
    parser.add_argument(
        '-t',
        '--threads',
        type=int,
        default=50,
        help='Maximum number of client threads')
    parser.add_argument(
        '-V',
        '--version',
        default='SSH-2.0-OpenSSH_6.6.1p1 Debian-5',
        help='SSH local version to advertise')
    parser.add_argument(
        '-v',
        '--verbose',
        default=False,
        action="count",
        help="Show verbose output, use multiple times increase verbosity")
    parser.add_argument(
        '-D',
        '--daemon',
        default=False,
        action="store_true",
        help="Run as unix daemon")

    args = parser.parse_args()
    if not os.path.isabs(args.output):
        args.output = os.path.join(os.getcwd(), args.output)

    if not os.path.isabs(args.key):
        args.key = os.path.join(os.getcwd(), args.key)

    if not os.path.isabs(args.log):
        args.log = os.path.join(os.getcwd(), args.log)

    server = Pshitt(args)
    if args.daemon:
        with daemon.DaemonContext():
            server.run(args)
    else:
        server.run(args)


if __name__ == '__main__':
    main()
