#!/usr/bin/env python
#-*- coding: utf-8 -*-

import RPi.GPIO as GPIO

import threading
import time
import os
import socket
import json
import signal

import config

class Status:
	status = 0
	level = 0

class GracefulKiller:
	kill = False
	def __init__(self):
		signal.signal(signal.SIGINT, self.exit)
		signal.signal(signal.SIGTERM, self.exit)

	def exit(self, signum, frame):
		self.kill = True

class CommThread(threading.Thread):
	def __init__(self, status_lock, config_lock):
		super(CommThread, self).__init__()
		self.status_lock = status_lock
		self.config_lock = config_lock
		self.interrupt = threading.Event()

	def run(self):
		s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
		try:
			os.remove("/tmp/pokecan.sock")
		except OSError:
			pass
		
		s.bind("/tmp/pokecan.sock")
		s.listen(1)
		s.settimeout(1)
		while not self.interrupt.isSet():
			try:
				conn, addr = s.accept()
			except socket.timeout:
				continue

			data = conn.recv(1024)
			if not data:
				conn.close()
				continue

			res = {}
			try:
				req = json.loads(data)
				if req["command"] == "status":
					with self.status_lock:
						res = {"status": Status.status, "level": Status.level}
				elif req["command"] == "read_config":
					with self.config_lock:
						res = {"status": "ok", "bin_height": config.bin_height, "lift_height": config.lift_height}
				elif req["command"] == "set_config":
					res = {"status": "ok"}
				else:
					res = {"status": "error", "message:": "invalid command"}
			except ValueError:
				res = {"status": "error", "message:": "invalid request"}

			conn.send(json.dumps(res))
			conn.close()
	
	def join(self, timeout=None):
		self.interrupt.set()
		super(CommThread, self).join(timeout)
	
class WorkerThread(threading.Thread):
	pins = {"trig": 11, "echo": 13}

	def __init__(self, status_lock, config_lock):
		super(WorkerThread, self).__init__()
		self.status_lock = status_lock
		self.config_lock = config_lock
		self.interrupt = threading.Event()

	def run(self):
		GPIO.setmode(GPIO.BOARD)
		GPIO.setup(self.pins["trig"], GPIO.OUT)
		GPIO.setup(self.pins["echo"], GPIO.IN)

		time.sleep(0.01)

		while not self.interrupt.isSet():
			GPIO.output(self.pins["trig"], True)
			time.sleep(0.00001)
			GPIO.output(self.pins["trig"], False)

			while GPIO.input(self.pins["echo"]) == 0:
				pulse_start = time.time()
			while GPIO.input(self.pins["echo"]) == 1:
				pulse_end = time.time()

			if (not 'pulse_start' in locals()) or (not 'pulse_end' in locals()):
				distance = 1000
			else:
				pulse_duration = pulse_end - pulse_start
				distance = pulse_duration * 17150

			with self.status_lock, self.config_lock:
				if distance > config.bin_height:
					Status.level = 0
				else:
					Status.level = round((config.bin_height - distance) / config.bin_height * 100)

			time.sleep(1)

		GPIO.cleanup()
	
	def join(self, timeout=None):
		self.interrupt.set()
		super(WorkerThread, self).join(timeout)

if __name__ == "__main__":
	pid = os.getpid()
	try:
		f = open("/var/run/pokecan-master.pid", "w")
		f.write(str(pid))
		f.close()
	except IOError:
		pass

	status_lock = threading.Lock()
	config_lock = threading.Lock()
	
	config.load()

	commthread = CommThread(status_lock, config_lock)
	commthread.start()

	workerthread = WorkerThread(status_lock, config_lock)
	workerthread.start()

	print "All threads started."

	killer = GracefulKiller()

	while True:
		time.sleep(1)
		if killer.kill: break

	print "Stopping master."
