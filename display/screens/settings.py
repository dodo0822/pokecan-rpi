import constants
from fonts import font, font_status, font_time

from comms import master_cmd

class SettingsScreen():
	menu_items = ["Route", "Motor Test", "Calibrate", "Threshold", "Manual Dump", "Reboot", "Factory Reset"]

	def __init__(self):
		self.selected = 0
		self.scroll_top = 0
		self.scroll_bot = 4 if len(self.menu_items) > 4 else len(self.menu_items)

	def render(self, draw):
		draw.rectangle((0, 0, 128, 64), outline=0, fill=0)
		draw.text((0, 0), "Pokecan Settings", fill=255, font=font_status)
		for i in range(self.scroll_top, self.scroll_bot):
			if self.selected == i:
				line = "> "
			else:
				line = "   "

			line += self.menu_items[i]
			draw.text((0, 14+((i-self.scroll_top)*12)), line, fill=255, font=font)
			
	def key(self, key):
		global scr
		if key == 2:
			return constants.SCR_MENU
		elif key == 0:
			if self.selected > 0:
				self.selected -= 1
				if self.selected < self.scroll_top:
					self.scroll_top -= 1
					self.scroll_bot -= 1
		elif key == 1:
			if self.selected < (len(self.menu_items)-1):
				self.selected += 1
				if self.selected >= self.scroll_bot:
					self.scroll_top += 1
					self.scroll_bot += 1
		elif key == 3:
			if self.selected == 0:
				return constants.SCR_ROUTE
			elif self.selected == 1:
				return constants.SCR_MOTOR_TEST
			elif self.selected == 2:
				return constants.SCR_CALIBRATION
			elif self.selected == 3:
				return constants.SCR_DUMP_TH
			elif self.selected == 4:
				master_cmd({"command":"set_request"})

		return constants.SCR_NONE