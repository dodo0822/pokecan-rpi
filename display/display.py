#!/usr/bin/env python
# -*- coding: utf-8 -*-

from oled.device import ssd1306, sh1106
from oled.render import canvas
from PIL import ImageFont, ImageDraw, Image
from time import sleep, time
from Adafruit_GPIO.MCP230xx import MCP23008
import RPi.GPIO as GPIO
import json, os

import constants

from screens.main import MainScreen
from screens.menu import MenuScreen
from screens.about import AboutScreen
from screens.network import NetworkScreen
from screens.settings import SettingsScreen
from screens.dump import DumpingThresholdScreen
from screens.cali import CalibrationScreen
from screens.route import RouteScreen
from screens.motortest import MotorTestScreen

from fonts import font, font_status, font_time

GPIO.setmode(GPIO.BOARD)
GPIO.setup(7, GPIO.IN, pull_up_down=GPIO.PUD_UP)

mcp = MCP23008(address = 0x20)
for i in range(0, 4):
	mcp.setup(i, GPIO.IN)
	mcp.pullup(i, 1)

key_pressed = [False, False, False, False]

device = ssd1306(port=1, address=0x3C)

with canvas(device) as draw:
	draw.rectangle((0, 0, device.width, device.height), outline=0, fill=0)
	logo = Image.open("images/pokecan.png")
	draw.bitmap((0, 0), logo, fill=255)
	draw.text((10, 45), "by Dodo, Pierre, Sasa", fill=255, font=font)
	
sleep(1)
		
scr = MainScreen()

while True:
	pressed = -1
	for i in range(0, 4):
		read = ((mcp.input(i)) - 1) * -1
		if read == 1:
			if not key_pressed[i]:
				key_pressed[i] = True
				pressed = i
				break
		else:
			key_pressed[i] = False

	if pressed >= 0:
		ret = scr.key(pressed)
		if ret == constants.SCR_MAIN:
			scr = MainScreen()
		elif ret == constants.SCR_MENU:
			scr = MenuScreen()
		elif ret == constants.SCR_SETTINGS:
			scr = SettingsScreen()
		elif ret == constants.SCR_NETWORK:
			scr = NetworkScreen()
		elif ret == constants.SCR_ABOUT:
			scr = AboutScreen()
		elif ret == constants.SCR_DUMP_TH:
			scr = DumpingThresholdScreen()
		elif ret == constants.SCR_CALIBRATION:
			scr = CalibrationScreen()
		elif ret == constants.SCR_ROUTE:
			scr = RouteScreen()
		elif ret == constants.SCR_MOTOR_TEST:
			scr = MotorTestScreen()

	with canvas(device) as draw:
		scr.render(draw)

	sleep(0.05)
