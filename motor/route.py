from comms import master_cmd
from time import sleep
from constants import hall_scalar

import RPi.GPIO as GPIO

master_cmd({"command":"set_status","status":0})
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

def full_route():
	global current_distance, mode
	resp = master_cmd({"command":"dump_config"})
	route = resp["route"]
	master_cmd({"command":"set_status","status":1})

	GPIO.output(23, GPIO.HIGH)
	sleep(0.4)
	GPIO.output(23, GPIO.LOW)

	# 1> MOVE
	for seg in route:
		current_distance = 0
		print "Move - " + str(seg)
		if seg["direction"] == 0:
			mode = 0
			master_cmd({"command":"motor","motor":2,"direction":1})
			master_cmd({"command":"motor","motor":3,"direction":1})
		elif seg["direction"] == 1:
			mode = 1
			master_cmd({"command":"motor","motor":2,"direction":1})
			master_cmd({"command":"motor","motor":3,"direction":-1})

		while (current_distance + 7) < seg["distance"]:
			sleep(0.1)

		master_cmd({"command":"stop_all_motors"})
		sleep(1)

	master_cmd({"command":"set_status","status":2})

	# 2> LIFT
	master_cmd({"command":"motor","motor":4,"direction":1})
	master_cmd({"command":"motor","motor":5,"direction":1})
	while GPIO.input(24):
		sleep(0.1)

	master_cmd({"command":"motor","motor":4,"direction":-1})
	master_cmd({"command":"motor","motor":5,"direction":-1})
	while not GPIO.input(24):
		sleep(0.05)

	master_cmd({"command":"stop_all_motors"})

	# 3> DUMP
	master_cmd({"command":"motor","motor":6,"direction":-1})
	master_cmd({"command":"motor","motor":7,"direction":-1})

	sleep(2.9)

	master_cmd({"command":"stop_all_motors"})

	sleep(1)

	master_cmd({"command":"motor","motor":6,"direction":1})
	master_cmd({"command":"motor","motor":7,"direction":1})

	sleep(2.9)

	master_cmd({"command":"stop_all_motors"})

	# 4> DOWN
	master_cmd({"command":"motor","motor":4,"direction":-1})
	master_cmd({"command":"motor","motor":5,"direction":-1})
	while GPIO.input(26):
		sleep(0.1)

	master_cmd({"command":"motor","motor":4,"direction":1})
	master_cmd({"command":"motor","motor":5,"direction":1})
	while not GPIO.input(26):
		sleep(0.05)

	master_cmd({"command":"stop_all_motors"})
	master_cmd({"command":"set_status","status":1})

	# 5> TURN AROUND
	print "5"

	current_distance = 0
	mode = 1
	around_distance = 180
	if len(route) > 0:
		if route[-1]["direction"] == 1 and route[-1]["distance"] < 180:
			around_distance = 180 - route[-1]["distance"]
			route.pop()

	master_cmd({"command":"motor","motor":2,"direction":1})
	master_cmd({"command":"motor","motor":3,"direction":-1})
	while (current_distance + 7) < around_distance:
		sleep(0.1)

	master_cmd({"command":"stop_all_motors"})

	sleep(1)


	# 6> GO BACK
	print "6"
	for seg in route:
		current_distance = 0
		print "Move - " + str(seg)
		if seg["direction"] == 0:
			mode = 0
			master_cmd({"command":"motor","motor":2,"direction":1})
			master_cmd({"command":"motor","motor":3,"direction":1})
		elif seg["direction"] == 1:
			seg["distance"] = 360 - seg["distance"]
			mode = 1
			master_cmd({"command":"motor","motor":2,"direction":1})
			master_cmd({"command":"motor","motor":3,"direction":-1})

		while (current_distance + 7) < seg["distance"]:
			sleep(0.1)

		master_cmd({"command":"stop_all_motors"})
		sleep(1)

	# 7> TURN AROUND AGAIN

	current_distance = 0
	mode = 1
	around_distance = 180

	master_cmd({"command":"motor","motor":2,"direction":1})
	master_cmd({"command":"motor","motor":3,"direction":-1})
	while (current_distance + 7) < around_distance:
		sleep(0.1)


	master_cmd({"command":"stop_all_motors"})

	print "Completed!"

	for i in range(3):
		GPIO.output(23, GPIO.HIGH)
		sleep(0.15)
		GPIO.output(23, GPIO.LOW)
		sleep(0.15)
		
	master_cmd({"command":"set_status","status":0})
	pass

GPIO.setmode(GPIO.BOARD)

GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(23, GPIO.OUT)

while True:
	GPIO.remove_event_detect(16)
	GPIO.remove_event_detect(18)
	GPIO.add_event_detect(16, GPIO.BOTH, callback=move_hall_edge, bouncetime=5)
	GPIO.add_event_detect(18, GPIO.BOTH, callback=move_hall_edge, bouncetime=5)
	resp = master_cmd({"command":"status"})
	if resp["requested"]:
		master_cmd({"command":"proc_request"})
		full_route()
	sleep(0.5);