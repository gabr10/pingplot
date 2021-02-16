#!/usr/bin/env python

VERSION='1.1'

try:
	from Queue import Queue, Empty
except ImportError:
	from queue import Queue, Empty

from threading import Thread
from subprocess import Popen, PIPE
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from datetime import datetime
import sys
import signal
import random
from itertools import count
import pandas as pd
from matplotlib.animation import FuncAnimation

def enqueue_output(out, err, queue):
	try:
		for line in iter(out.readline, b''):
			try:
				l = float(line.decode('utf-8').split(' ')[6].split('=')[1])
				data = (datetime.now(), l)
				queue.put(data)
				#print(repr(data))
				print('ping..')
			except Exception:
				print(line)
				# print(e)
	except:
		print("Error reading from ping", err.readlines())
	finally:
		out.close()
		err.close()

def signal_handler(signal, frame):
	print('Execution canceled manually. Thanks for using me!')
	sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

if __name__ == "__main__":
	ping_args = sys.argv[1:]

	p = Popen(['ping']+ping_args, stdout=PIPE,
			  stderr=PIPE, bufsize=1, close_fds=True)
	q = Queue()
	t = Thread(target=enqueue_output, args=(p.stdout, p.stderr, q))
	t.daemon = True  # thread dies with the program
	t.start()

	xdata = np.array([])
	ydata = np.array([])

	def get_data():
		global xdata
		global ydata
		while True:
			try:
				x, y = q.get_nowait()
				xdata = np.append(xdata, [x,])
				ydata = np.append(ydata, [y,])
			except Empty:
				return (xdata, ydata)


	plt.style.use('fivethirtyeight')
	
	x_vals = []
	y_vals = []

	index = count()


	def animate(i):
		x, y1 = get_data()
		print('Ping count so far: ' + str(len(x)))

		plt.cla()

		plt.plot(x, str(y1) + 'ms', label=sys.argv[1])

		plt.legend(loc='upper left')
		plt.tight_layout()


	plt.title('Ping times')
	plt.xlabel('Time')
	plt.ylabel('ICMP Response (ms)')
	ani = FuncAnimation(plt.gcf(), animate, interval=1000)

	plt.tight_layout()
	plt.show()