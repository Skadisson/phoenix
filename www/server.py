import os
import yaml
import http.server
import socketserver

path = os.path.join("..", "env", "service.yaml")
file = open(path, "r", encoding='utf8')
service_yaml = yaml.load(file, Loader=yaml.FullLoader)
PORT = service_yaml['port_webserver']
Handler = http.server.SimpleHTTPRequestHandler
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print("serving at port", PORT)
    httpd.serve_forever()
    Handler.send_header('Access-Control-Allow-Origin', '*')
