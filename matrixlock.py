#!/usr/bin/python3

from argparse import ArgumentParser
from http.server import BaseHTTPRequestHandler, HTTPServer
from os.path import dirname, join
from subprocess import run, Popen, DEVNULL
from threading import Thread, Event
from time import time

import json

def main(matrix_delay_secs):
	workspaces = get_workspaces()
	visible = [ws for ws in workspaces if ws['visible']]
	with SubprocessServer(('', 0), len(visible)) as server:
		port = server.server_address[1]
		for ws in visible:
			overlay_matrix_on_workspace(ws['name'], port, matrix_delay_secs)
	run(['i3lock', '-n'], check=True)
	for pid_path in server.received_posts:
		assert pid_path.startswith('/'), pid_path
		try:
			pid = int(pid_path[1:])
		except ValueError:
			continue
		run(['kill', str(pid)])

def get_workspaces():
	cp = run(
		['i3-msg', '-t', 'get_workspaces'],
		capture_output=True, check=True, text=True
	)
	return json.loads(cp.stdout)

def overlay_matrix_on_workspace(ws_name, port, delay):
	run([
		'i3-msg',
		f'workspace {ws_name}; '
		# There may already be a full-screen app on that workspace.
		# This would prevent us from showing the Matrix full-screen.
		# So disable fullscreen first.
		f'fullscreen disable; '
		# --color-text=black to hide the cursor when there is a delay.
		f'exec "xfce4-terminal --hide-scrollbar --hide-menubar --fullscreen --color-text=black '
		# Send child PID to server so the parent can kill it, then show Matrix:
		f'-x bash -c \'curl -X POST localhost:{port}/$$ && sleep {delay} && cmatrix -b\'"'
	], check=True, stdout=DEVNULL)

class SubprocessServer(HTTPServer):
	"""
	Process up to num_requests POST requests in up to timeout_secs seconds and
	store their paths in self.received_posts.
	"""
	def __init__(self, server_address, num_requests, timeout_secs=5):
		super().__init__(server_address, SubprocessHandler)
		self.received_posts = []
		self._num_requests = num_requests
		self._timeout_secs = timeout_secs
		self._thread = Thread(target=self._run_in_thread)
		self._started = Event()
		self._timeout_encountered = False
	def __enter__(self):
		result = super().__enter__()
		self._thread.start()
		self._started.wait()
		return result
	def __exit__(self, *args, **kwargs):
		self._thread.join()
	def _run_in_thread(self):
		self._started.set()
		end = time() + self._timeout_secs
		for _ in range(self._num_requests):
			time_remaining = end - time()
			if time_remaining < 0:
				break
			self.timeout = time_remaining
			self.handle_request()
			if self._timeout_encountered:
				break
	def handle_timeout(self):
		self._timeout_encountered = True

class SubprocessHandler(BaseHTTPRequestHandler):
	def do_POST(self):
		self.server.received_posts.append(self.path)
		self.send_response(200)
		self.end_headers()
	def log_message(self, format, *args):
		return

if __name__ == '__main__':
	parser = ArgumentParser(description='Alternative to i3lock that displays the Matrix')
	parser.add_argument(
		'delay', type=int, nargs='?', default=0,
		help='Seconds between blanking out the screen and starting the Matrix'
	)
	args = parser.parse_args()
	main(args.delay)
