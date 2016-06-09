import RPi.GPIO as GPIO

from time import sleep

def edge(channel):
	print "EDGE!!"

GPIO.setmode(GPIO.BOARD)
GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.remove_event_detect(24)
#GPIO.remove_event_detect(18)
GPIO.add_event_detect(24, GPIO.BOTH, callback=edge, bouncetime=200)

while True:
	sleep(1)