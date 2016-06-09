import constants
from fonts import font, font_status, font_time

from comms import master_cmd

import RPi.GPIO as GPIO

class MotorTestScreen:
	def __init__(self):
		self.menu_items = [ "Forward", "Backward", "Leftward", "Rightward", "Both Up", "Both Down", "L Up", "L Down", "R Up", "R Down", "D Both Up", "D Both Down", "D L Up", "D L Down", "D R Up", "D R Down", "Turn CW", "Turn CCW" ]
		self.selected = 0
		self.scroll_top = 0
		self.scroll_bot = 5
		master_cmd({"command":"stop_all_motors"})
		GPIO.add_event_detect(7, GPIO.BOTH, callback=self.btn_edge, bouncetime=250)

	def btn_edge(self, channel):
		if GPIO.input(7):
			print "Released!"
			master_cmd({"command":"stop_all_motors"})
		else:
			if self.selected == 0:
				master_cmd({"command":"motor","motor":2,"direction":1})
				master_cmd({"command":"motor","motor":3,"direction":1})
			elif self.selected == 1:
				master_cmd({"command":"motor","motor":2,"direction":-1})
				master_cmd({"command":"motor","motor":3,"direction":-1})
			elif self.selected == 2:
				master_cmd({"command":"motor","motor":0,"direction":1})
				master_cmd({"command":"motor","motor":1,"direction":1})
			elif self.selected == 3:
				master_cmd({"command":"motor","motor":0,"direction":-1})
				master_cmd({"command":"motor","motor":1,"direction":-1})
			elif self.selected == 4:
				master_cmd({"command":"motor","motor":4,"direction":1})
				master_cmd({"command":"motor","motor":5,"direction":1})
			elif self.selected == 5:
				master_cmd({"command":"motor","motor":4,"direction":-1})
				master_cmd({"command":"motor","motor":5,"direction":-1})
			elif self.selected == 6:
				master_cmd({"command":"motor","motor":4,"direction":1})
			elif self.selected == 7:
				master_cmd({"command":"motor","motor":4,"direction":-1})
			elif self.selected == 8:
				master_cmd({"command":"motor","motor":5,"direction":1})
			elif self.selected == 9:
				master_cmd({"command":"motor","motor":5,"direction":-1})
			elif self.selected == 10:
				master_cmd({"command":"motor","motor":6,"direction":1})
				master_cmd({"command":"motor","motor":7,"direction":1})
			elif self.selected == 11:
				master_cmd({"command":"motor","motor":6,"direction":-1})
				master_cmd({"command":"motor","motor":7,"direction":-1})
			elif self.selected == 12:
				master_cmd({"command":"motor","motor":6,"direction":1})
			elif self.selected == 13:
				master_cmd({"command":"motor","motor":6,"direction":-1})
			elif self.selected == 14:
				master_cmd({"command":"motor","motor":7,"direction":1})
			elif self.selected == 15:
				master_cmd({"command":"motor","motor":7,"direction":-1})
			elif self.selected == 16:
				master_cmd({"command":"motor","motor":2,"direction":1})
				master_cmd({"command":"motor","motor":3,"direction":-1})
			elif self.selected == 17:
				master_cmd({"command":"motor","motor":2,"direction":-1})
				master_cmd({"command":"motor","motor":3,"direction":1})


	def render(self, draw):
		draw.rectangle((0, 0, 128, 64), outline=0, fill=0)
		draw.text((0, 0), "Motor Test", fill=255, font=font_status)
		for i in range(self.scroll_top, self.scroll_bot):
			if self.selected == i:
				line = "> "
			else:
				line = "   "

			line += self.menu_items[i]
			draw.text((0, 14+((i-self.scroll_top)*9)), line, fill=255, font=font_time)

	def key(self, key):
		global scr
		if key == 0 and self.selected > 0:
			self.selected -= 1
			if self.selected < self.scroll_top:
				self.scroll_bot -= 1
				self.scroll_top -= 1
			return constants.SCR_NONE
		elif key == 1 and self.selected < (len(self.menu_items) - 1):
			self.selected += 1
			if self.selected >= self.scroll_bot:
				self.scroll_bot += 1
				self.scroll_top += 1
			return constants.SCR_NONE
		elif key == 2:
			GPIO.remove_event_detect(7)
			return constants.SCR_MENU

		return constants.SCR_NONE