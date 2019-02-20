#!/usr/bin/python3

import http.server
import json
import ssl
import sys

SERVERNAME = 'borrel.collegechaos.nl'
PORTPLAIN = 1897
PORTSSL = 2003
CERTFILE = 'fullchain.pem'
KEYFILE = 'privkey.pem'

class ChaosRequestHandler(http.server.BaseHTTPRequestHandler):
    def do_HEAD(self):
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
    def do_GET(self):
        if self.server.scoredump is None:
            self.send_response(204)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
        else:
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(self.server.scoredump)
    def do_POST(self):
        scoredump = self.rfile.read(int(self.headers.get('Content-Length')))
        
        print("POST: {}".format(scoredump))
        try:
            json.loads(scoredump.decode())
            self.server.scoredump = scoredump
        except Exception as e:
            print(e)
        self.send_response(204)
        self.end_headers()

if __name__ == "__main__":
    if "--http" in sys.argv:
        server = http.server.HTTPServer((SERVERNAME, PORTPLAIN), ChaosRequestHandler)
    else:
        server = http.server.HTTPServer((SERVERNAME, PORTSSL), ChaosRequestHandler)
        server.socket = ssl.wrap_socket(
            server.socket,
            server_side=True,
            certfile=CERTFILE,
            keyfile=KEYFILE,
            ssl_version=ssl.PROTOCOL_TLSv1_2)
    server.scoredump = None
    server.serve_forever()
