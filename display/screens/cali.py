from comms import master_cmd
from time import time

import constants
from fonts import font, font_status, font_time

class CalibrationScreen:
	def __init__(self):
		self.previous_update = time()
		res = master_cmd({"command":"status"})
		if res == "":
			self.distance = -1
		else:
			self.distance = int(res["distance"])

	def render(self, draw):
		draw.rectangle((0, 0, 128, 64), outline=0, fill=0)
		draw.text((0, 0), "Calibration", fill=255, font=font_status)
		if (time() - self.previous_update) > 1:
			self.previous_update = time()
			res = master_cmd({"command":"status"})
			if res == "":
				self.distance = -1
			else:
				self.distance = int(res["distance"])

		if self.distance == -1:
			draw.text((0, 28), "Can't connect to master", fill=255, font=font)
			draw.text((0, 38), "Retrying..", fill=255, font=font)
		else:
			draw.text((52, 20), ("{0:g}".format(self.distance) + " cm"), fill=255, font=font_status)

	def key(self, key):
		global scr
		if key == 2:
			return constants.SCR_SETTINGS

		if self.distance > 0:
			if key == 3:
				master_cmd({"command":"write_config","name":"bin_height","value":self.distance});
				return constants.SCR_SETTINGS

		return constants.SCR_NONE