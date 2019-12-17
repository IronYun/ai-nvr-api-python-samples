# The MIT License
#
# Copyright (c) Ironyun, Inc. http://www.ironyun.com
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from http.server import BaseHTTPRequestHandler,HTTPServer
from urllib import parse
import json

class myHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        print ("Alert Received...")
        if self.path.startswith("/alert"):			
            if "?" in self.path:
                parse_result = parse.urlparse(self.path)
                query_components = parse.parse_qs(parse_result.query)
                for key,value in query_components.items():
                    print("%s = %s" %(key,value))
							
            content_len = int(self.headers.get('Content-Length'))
            post_body = self.rfile.read(content_len)
            post_body_json = json.loads(post_body)
            print (post_body_json)
                            
            self.send_response(200)
            self.send_header('Content-type','text/html')
            self.end_headers()			
        return

if __name__ == "__main__":
	try:
		server = HTTPServer(('', 7777), myHandler)
		print ('Started httpserver on port ' , 7777)
	
		server.serve_forever()
	except KeyboardInterrupt:
		print ('^C received, shutting down the web server')
		server.socket.close()

