import http.server
import socketserver
from bin.service import Environment

env = Environment.Environment()
PORT = env.get_server_port()
Handler = http.server.SimpleHTTPRequestHandler
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print("serving at port", PORT)
    httpd.serve_forever()
    Handler.send_header('Access-Control-Allow-Origin', '*')
