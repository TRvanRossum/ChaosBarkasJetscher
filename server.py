#!/usr/bin/python3

import http.server
import json

SERVERNAME = ('borrel.collegechaos.nl', 2003)

class ChaosRequestHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.server.scoredump is None:
            self.send_response(204)
            self.end_headers()
        else:
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
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
    server = http.server.HTTPServer(SERVERNAME, ChaosRequestHandler)
    server.scoredump = None
    server.serve_forever()
