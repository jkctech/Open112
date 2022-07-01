import os
import json

from http.server import BaseHTTPRequestHandler, HTTPServer

def RequestHandlerFactory(webroot, msglist):
	class RequestHandler(BaseHTTPRequestHandler):

		rewrites = {
			"/": "/index.html",
			"/stats": "/stats.html"
		}

		def do_GET(self):
			try:
				files = self.getfiles()

				# Unify directory delimiters
				path = self.path.replace('\\', '/').split('?')[0]

				# Special cases
				if path == "/messages":
					self.messages()
					return

				# Rewrites
				if path in self.rewrites.keys():
					path = self.rewrites[path]

				# Prepend webroot so relative path makes sense
				path = webroot + path

				# If path is in webroot, display it!
				if path in files:
					self.send_response(200)
					# self.send_header("Content-type", "text/html")
					self.end_headers()

					with open(path, "rb") as f:
						self.wfile.write(f.read())

				# 404
				else:
					self.send_response(404)
					self.end_headers()

					with open(webroot + "/404.html", "rb") as f:
						self.wfile.write(f.read())

			except ConnectionAbortedError:
				pass

		# Disable logging to the stdout
		def log_message(self, format, *args):
			return

		# Simple way to prevent directory traversal
		def getfiles(self):
			result = []
			for root, subdirs, files in os.walk(webroot):
				for filename in files:
					file_path = os.path.join(root, filename)
					result.append(file_path)
			return result

		# Display last messages in JSON
		def messages(self):
			self.send_response(200)
			self.send_header("Content-type", "application/json")
			self.end_headers()
			self.wfile.write(bytes(json.dumps(msglist()), "utf-8"))

	return RequestHandler

class DisplayServer(HTTPServer):

	def __init__(self, hostname, port, webroot, msglist):
		super().__init__((hostname, port), RequestHandlerFactory(webroot, msglist))
