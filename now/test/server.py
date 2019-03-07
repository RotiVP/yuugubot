from http.server import HTTPServer
import sys
sys.path.insert(0, '../')
from index import handler

serv = HTTPServer(("localhost", 80), handler)
serv.serve_forever()
