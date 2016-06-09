from comms import master_cmd

from Adafruit_GPIO.MCP230xx import MCP23017
import Adafruit_PCA9685
import RPi.GPIO as GPIO

from constants import invert, multiplier
from time import sleep

import os

mcp = MCP23017(address = 0x24)
for i in range(0, 16):
	mcp.setup(i, GPIO.OUT)

pca = Adafruit_PCA9685.PCA9685()
pca.set_pwm_freq(500)

for i in range(8):
	pca.set_pwm(i, 0, int(4095*multiplier[i]))

def stop_all():
	for i in range(0, 8):
		stop(i)

def stop(i):
	if i < 4:
		mcp.output(i*2, GPIO.LOW)
		mcp.output(i*2+1, GPIO.LOW)
	else:
		pca.set_pwm(i*2, 0, 0)
		pca.set_pwm(i*2+1, 0, 0)

def move(i, direction):
	if direction == 1:
		print invert
		if invert[i]:
			if i < 4:
				mcp.output(i*2, GPIO.LOW)
				mcp.output(i*2+1, GPIO.HIGH)
			else:
				pca.set_pwm(i*2, 0, 0)
				pca.set_pwm(i*2+1, 0, 4095)
		else:
			if i < 4:
				mcp.output(i*2, GPIO.HIGH)
				mcp.output(i*2+1, GPIO.LOW)
			else:
				pca.set_pwm(i*2, 0, 4095)
				pca.set_pwm(i*2+1, 0, 0)
	elif direction == -1:
		if not invert[i]:
			if i < 4:
				mcp.output(i*2, GPIO.LOW)
				mcp.output(i*2+1, GPIO.HIGH)
			else:
				pca.set_pwm(i*2, 0, 0)
				pca.set_pwm(i*2+1, 0, 4095)
		else:
			if i < 4:
				mcp.output(i*2, GPIO.HIGH)
				mcp.output(i*2+1, GPIO.LOW)
			else:
				pca.set_pwm(i*2, 0, 4095)
				pca.set_pwm(i*2+1, 0, 0)
	else:
		stop(i)

stop_all()

motors = [0, 0, 0, 0, 0, 0, 0, 0]

while True:
	sleep(0.1)
	resp = master_cmd({"command":"get_motors"})
	if resp["status"] != "ok": continue

	new_motors = resp["motors"]
	for i in range(8):
		if not motors[i] == new_motors[i]:
			print "move motor" + str(i)
			move(i, new_motors[i])
			motors[i] = new_motors[i]
