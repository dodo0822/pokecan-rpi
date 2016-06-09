from time import strftime, time
from fonts import font, font_status, font_time
from PIL import Image

from comms import master_cmd

import json

import socket
import constants

trashcan = Image.open("images/trashcan.png")

class MainScreen:
	def __init__(self):
		self.previous_update = 0
		self.status = -1
		self.level = 0

	def render(self, draw):
		draw.rectangle((0, 0, 128, 64), outline=0, fill=0)
		draw.text((20, 0), strftime("%Y-%m-%d %H:%M:%S"), fill=255, font=font_time)
		draw.line([(0, 12), (128, 12)], fill=255, width=1)

		if (time() - self.previous_update) < 1:
			if self.status == -1:
				draw.text((0, 28), "Can't connect to master", fill=255, font=font)
				draw.text((0, 38), "Retrying..", fill=255, font=font)
				return
			elif self.status == 0:
				draw.text((13, 28), "Idle", fill=255, font=font_status)
			elif self.status == 1:
				draw.text((13, 28), "Move", fill=255, font=font_status)
			elif self.status == 2:
				draw.text((13, 28), "Dump", fill=255, font=font_status)
			
			draw.bitmap((80, 15), trashcan, fill=255)
			draw.text((45, 50-(35*self.level/100)), ("{0:g}".format(self.level) + "% -").rjust(6, " "), fill=255, font=font)
			return

		self.previous_update = time()

		res = master_cmd({"command":"status"})

		if res == "":
			draw.text((0, 28), "Can't connect to master", fill=255, font=font)
			draw.text((0, 38), "Retrying..", fill=255, font=font)
			self.status = -1
		else:
			self.status = res["status"]
			self.level = res["level"]
			if res["status"] == 0:
				draw.text((13, 28), "Idle", fill=255, font=font_status)
			elif res["status"] == 1:
				draw.text((13, 28), "Move", fill=255, font=font_status)
			elif res["status"] == 2:
				draw.text((13, 28), "Dump", fill=255, font=font_status)

			draw.bitmap((80, 15), trashcan, fill=255)
			draw.text((45, 50-(35*res["level"]/100)), ("{0:g}".format(res["level"]) + "% -").rjust(6, " "), fill=255, font=font)

	
	def key(self, key):
		if key == 3:
			return constants.SCR_MENU
		return constants.SCR_NONE
