import RPi.GPIO as GPIO
from comms import master_cmd
from time import sleep

from constants import hall_scalar

master_cmd({"command":"stop_all_motors"})

current_distance = 0
mode = 0

def move_hall_edge(channel):
	global current_distance, mode
	if mode == 0:
		print current_distance
		current_distance += hall_scalar[0]
	else:
		print current_distance
		current_distance += hall_scalar[1]

GPIO.setmode(GPIO.BOARD)

GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.remove_event_detect(16)
GPIO.remove_event_detect(18)
GPIO.add_event_detect(16, GPIO.BOTH, callback=move_hall_edge, bouncetime=5)
GPIO.add_event_detect(18, GPIO.BOTH, callback=move_hall_edge, bouncetime=5)

while True:
	direction = -1
	while not (direction >= 0 and direction <= 3):
		try:
			direction = input("Direction (0:F 1:B 2:CW 3:CCW) : ")
			if not isinstance(direction, int): direction = -1
		except SyntaxError:
			pass

	distance = -1
	while not (distance > 0):
		try:
			distance = input("Distance : ")
			if not isinstance(distance, int): distance = -1
		except SyntaxError:
			pass

	print "Move %d, %d" % (direction, distance)

	current_distance = 0

	if direction == 0:
		mode = 0
		master_cmd({"command":"motor","motor":2,"direction":1})
		master_cmd({"command":"motor","motor":3,"direction":1})
	elif direction == 1:
		mode = 0
		master_cmd({"command":"motor","motor":2,"direction":-1})
		master_cmd({"command":"motor","motor":3,"direction":-1})
	elif direction == 2:
		mode = 1
		master_cmd({"command":"motor","motor":2,"direction":1})
		master_cmd({"command":"motor","motor":3,"direction":-1})
	else:
		mode = 1
		master_cmd({"command":"motor","motor":2,"direction":-1})
		master_cmd({"command":"motor","motor":3,"direction":1})

	while (current_distance + 7) < distance:
		sleep(0.1)

	master_cmd({"command":"stop_all_motors"})
