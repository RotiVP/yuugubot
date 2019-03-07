from http.server import BaseHTTPRequestHandler

import ybapi

class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type','text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write('pong'.encode())
        return

    def do_POST(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.end_headers() 

        self.wfile.write('pong'.encode())
        return

        #content_len = int(self.headers.get('Content-Length'))
        #body = self.rfile.read(content_len).decode('utf-8')

        #print(body)

        res = ybapi.handleReqbody(body)
        self.wfile.write(res.encode())

        return
