import os
import yaml
import ssl
import http.server
import socketserver

path = os.path.join("..", "env", "service.yaml")
file = open(path, "r", encoding='utf8')
service_yaml = yaml.load(file, Loader=yaml.FullLoader)
PORT = service_yaml['port_webserver']
use_ssl = service_yaml['use_ssl']
Handler = http.server.SimpleHTTPRequestHandler
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print("serving at port", PORT)
    if use_ssl is True:
        httpd.socket = ssl.wrap_socket(httpd.socket, server_side=True, certfile='../localhost.pem', ssl_version=ssl.PROTOCOL_TLS)
    httpd.serve_forever()
    Handler.send_header('Access-Control-Allow-Origin', '*')
