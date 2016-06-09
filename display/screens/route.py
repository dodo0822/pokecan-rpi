import constants
from fonts import font, font_status, font_time

from comms import master_cmd

class RouteScreen():
	def __init__(self):
		self.selected = 0
		res = master_cmd({"command":"dump_config"});
		if res == "":
			self.status = -1
		else:
			self.status = 0
			self.route = res["route"]
			self.build_menu()

	def build_menu(self):
		self.list_items = []
		for r in self.route:
			if r["direction"] == 0:
				self.list_items.append("FORWARD " + ("{0:g}".format(r["distance"])))
			elif r["direction"] == 1:
				self.list_items.append("TURN CW " + ("{0:g}".format(r["distance"])))

		self.list_items.append("Add..");
		self.list_items.append("Save..");

		self.selected = 0
		self.scroll_top = 0
		self.scroll_bot = 4 if (len(self.list_items) > 4) else len(self.list_items)

	def render(self, draw):
		draw.rectangle((0, 0, 128, 64), outline=0, fill=0)
		draw.text((0, 0), "Route defn.", fill=255, font=font_status)

		if self.status == -1:
			draw.text((0, 28), "Can't connect to master", fill=255, font=font)
			draw.text((0, 38), "Please retry..", fill=255, font=font)
		elif self.status == 0:
			for i in range(self.scroll_top, self.scroll_bot):
				if self.selected == i:
					line = "> "
				else:
					line = "   "

				line += self.list_items[i]
				draw.text((0, 14+((i-self.scroll_top)*12)), line, fill=255, font=font)
		elif self.status == 1:
			draw.text((30, 15), "Move", fill=255, font=font)
			if self.temp_segment["direction"] == 0:
				draw.text((0, 35), "FORWARD", fill=255, font=font_status)
			elif self.temp_segment["direction"] == 1:
				draw.text((0, 35), "TURN CW", fill=255, font=font_status)
		elif self.status == 2:
			draw.text((30, 15), "For", fill=255, font=font)
			if self.temp_segment["direction"] == 1:
				draw.text((0, 35), ("{0:g}".format(self.temp_segment["distance"])) + " deg", fill=255, font=font_status)
			else:
				draw.text((0, 35), ("{0:g}".format(self.temp_segment["distance"])) + " cm", fill=255, font=font_status)
		else:
			draw.text((0, 14), "Delete?", fill=255, font=font)
			draw.text((0, 26), "Left=CANCEL", fill=255, font=font)
			draw.text((0, 38), "Right=CONFIRM", fill=255, font=font)

	def key(self, key):
		if self.status == -1:
			if key == 2:
				return constants.SCR_SETTINGS
			else:
				return constants.SCR_NONE
		elif self.status == 0:
			if key == 0:
				if self.selected > 0:
					self.selected -= 1
					if self.selected < self.scroll_top:
						self.scroll_bot -= 1
						self.scroll_top -= 1
				return constants.SCR_NONE
			elif key == 1:
				if self.selected < (len(self.list_items) - 1):
					self.selected += 1
					if self.selected >= self.scroll_bot:
						self.scroll_bot += 1
						self.scroll_top += 1
				return constants.SCR_NONE
			elif key == 2:
				return constants.SCR_SETTINGS
			else:
				if self.selected == (len(self.list_items) - 1):
					master_cmd({"command":"write_config","name":"route","value":self.route})
					return constants.SCR_SETTINGS
				elif self.selected == (len(self.list_items) - 2):
					self.temp_segment = {"direction":0,"distance":0}
					self.status = 1
					return constants.SCR_NONE
				else:
					self.status = 3
					return constants.SCR_NONE
		elif self.status == 1:
			if key == 1:
				self.temp_segment["direction"] -= 1
				if self.temp_segment["direction"] < 0: self.temp_segment["direction"] = 1
			elif key == 0:
				self.temp_segment["direction"] += 1
				if self.temp_segment["direction"] > 1: self.temp_segment["direction"] = 0
			elif key == 2:
				self.status = 0
			else:
				self.status = 2
			return constants.SCR_NONE
		elif self.status == 2:
			if key == 1:
				if self.temp_segment["distance"] > 0: self.temp_segment["distance"] -= 5
			elif key == 0:
				self.temp_segment["distance"] += 5
			elif key == 2:
				self.status = 1
			else:
				self.route.append(self.temp_segment)
				self.build_menu()
				self.status = 0
			return constants.SCR_NONE
		elif self.status == 3:
			if key == 2:
				self.status = 0
			elif key == 3:
				self.route.pop(self.selected)
				self.build_menu()
				self.status = 0

			return constants.SCR_NONE

		return constants.SCR_NONE