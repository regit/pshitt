==============================================
Passwords of SSH Intruders Transferred to Text
==============================================

Introduction
============

pshitt is a lightweight fake SSH server designed to collect authentication
data sent by intruders. It basically collect username and password used
by SSH bruteforce and write the extracted data to a file in JSON format.

Running pshitt
==============

Go into the source directory and run ::

 ./pshitt -o passwords.json

This will run a fake SSH server listening on port 2200 to catch authentication
data sent by the intruders. Information about SSH connection attempt will be
stored in the ``passwords.json`` using JSON as format ::

 {"username": "root", "src_ip": "116.10.191.184", "password": "P@ssword", \
  "src_port": 41397, "timestamp": "2014-06-25T21:35:21.660303"}

Full options are available via '-h' option ::

 usage: pshitt [-h] [-o OUTPUT] [-k KEY] [-l LOG] [-p PORT] [-t THREADS] [-v]
               [-D]
 
 Passwords of SSH Intruders Transferred to Text
 
 optional arguments:
   -h, --help            show this help message and exit
   -o OUTPUT, --output OUTPUT
                         File to export collected data
   -k KEY, --key KEY     Host RSA key
   -l LOG, --log LOG     File to log info and debug
   -p PORT, --port PORT  TCP port to listen to
   -t THREADS, --threads THREADS
                         Maximum number of client threads
   -v, --verbose         Show verbose output, use multiple times increase
                         verbosity
   -D, --daemon          Run as unix daemon
