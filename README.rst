======
PSHITT
======

Introduction
============

pshitt (for Passwords of SSH Intruders Transferred to Text) is a lightweight
fake SSH server designed to collect authentication data sent by intruders.
It basically collects username and password used by SSH bruteforce software
and writes the extracted data to a file in JSON format.

pshitt is written in Python and use paramiko to implement the SSH layer.

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

Using pshitt data
=================

As the format is JSON, it is easy to use the data in data analysis
software such as Splunk or Logstash.

Here's a sample configuration for logstash ::

 input {
    file {
       path => [ "/var/log/pshitt.log" ]
       codec =>   json
       type => "json-log"
    }
 }

 filter {
     # warn logstash that timestamp is the one to use
     if [type] == "json-log" {
         date {
             match => [ "timestamp", "ISO8601" ]
         }
     }

     # optional but geoip is interesting
     if [src_ip]  {
         geoip {
             source => "src_ip"
             target => "geoip"
             add_field => [ "[geoip][coordinates]", "%{[geoip][longitude]}" ]
             add_field => [ "[geoip][coordinates]", "%{[geoip][latitude]}"  ]
         }
         mutate {
             convert => [ "[geoip][coordinates]", "float" ]
         }
     }
 }

 output {
   elasticsearch {
        host => "localhost"
   }
 }

Basically, it is just enough to mention that the ``pshitt.log`` file is
using JSON format.
