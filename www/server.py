import http.server
import socketserver


PORT = 8090
Handler = http.server.SimpleHTTPRequestHandler
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print("serving at port", PORT)
    httpd.serve_forever()
    Handler.send_header('Access-Control-Allow-Origin', '*')