from http.server import BaseHTTPRequestHandler, HTTPServer
import json

class Server(HTTPServer):
    def __init__(self, address, request_handler):
        super().__init__(address, request_handler)


class RequestHandler(BaseHTTPRequestHandler):
    def __init__(self, request, client_address, server_class):
        self.server_class = server_class
        super().__init__(request, client_address, server_class)

    def do_GET(self):
        request_type = self.headers.get('type')

        if request_type == 'query':
            self.do_query()
        elif request_type == 'news':
            self.do_news()

    def do_query(self):
        data_string = self.headers.get('query')
        
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()

        print("{}".format(data_string))

        response_json = json.dumps({'type': 'query', 'content': 'the response'})
        
        self.wfile.write(response_json.encode())

    def do_news(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        
        response_json = json.dumps({'type': 'news', 'content' : [
            {'tag': 'Taxes', 'headline': 'Taxes raised by 500%'},
            {'tag': 'Parks', 'headline': 'All parks will be destroyed'},
            {'tag': 'Roads', 'headline': '$50 billion to build new roads that puncture tires'},
            {'tag': 'Transit', 'headline': '$10 trillion will be spent on new buses that will never arrive'},
        ]})
        
        self.wfile.write(response_json.encode())


def start_server(port, server_class=Server, handler_class=RequestHandler):
    server_address = ('', port)
    http_server = server_class(server_address, handler_class)
    print(f"Starting server on {''}:{port}")
    http_server.serve_forever()


def main():
    start_server(port=8000)


if __name__ == "__main__":
    main()
