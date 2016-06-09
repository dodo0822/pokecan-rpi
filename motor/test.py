from comms import master_cmd

from Adafruit_GPIO.MCP230xx import MCP23017
import Adafruit_PCA9685
import RPi.GPIO as GPIO

from constants import invert, multiplier

import os

mcp = MCP23017(address = 0x24)
for i in range(0, 16):
	mcp.setup(i, GPIO.OUT)

pca = Adafruit_PCA9685.PCA9685()
pca.set_pwm_freq(500)

current_distance = 0

def move_hall_edge(channel):
	global current_distance
	current_distance += 7.85

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

GPIO.setmode(GPIO.BOARD)

GPIO.setup(16, GPIO.IN)
GPIO.setup(18, GPIO.IN)

GPIO.remove_event_detect(16)
GPIO.remove_event_detect(18)
GPIO.add_event_detect(16, GPIO.BOTH, callback=move_hall_edge, bouncetime=5)
GPIO.add_event_detect(18, GPIO.BOTH, callback=move_hall_edge, bouncetime=5)

while True:
	print "1:Front 2:Rear 3:Left 4:Right 5:LLift 6:RLift 7:Lift 8:RDump 9:LDump 10:Dump 11: go left/right 12: turn cw/ccw"
	try:
		num = input("Enter number: ")
	except SyntaxError:
		continue
	if num < 1 or num > 12:
		continue

	print "1:Forward -1:Backward"
	try:
		direction = input("Enter direction: ")
	except SyntaxError:
		continue
	if direction < -1 or direction > 1:
		continue

	print str(num) + "," + str(direction)

	if num >= 1 and num <= 6:
		move(num - 1, direction)
	elif num == 7:
		move(4, direction)
		move(5, direction)
	elif num == 8:
		move(6, direction)
	elif num == 9:
		move(7, direction)
	elif num == 10:
		move(6, direction)
		move(7, direction)
	elif num == 11:
		move(2, direction)
		move(3, direction)
	elif num == 12:
		move(2, direction)
		move(3, direction*-1)

	try:
		input("Press enter to stop")
	except SyntaxError:
		pass

	print
	stop_all()