from PIL import Image

from comms import master_cmd

import constants
from fonts import font, font_status, font_time

class DumpingThresholdScreen:
	def __init__(self):
		res = master_cmd({"command":"dump_config"})
		if res == "":
			self.status = -1
		else:
			self.status = 0
			self.threshold = int(res["threshold"])

	def render(self, draw):
		draw.rectangle((0, 0, 128, 64), outline=0, fill=0)
		draw.text((0, 0), "Threshold", fill=255, font=font_status)
		if self.status == -1:
			draw.text((0, 28), "Can't connect to master", fill=255, font=font)
			draw.text((0, 38), "Please retry..", fill=255, font=font)
		else:
			draw.text((52, 20), str(self.threshold), fill=255, font=font_status)

	def key(self, key):
		global scr
		if key == 2:
			return constants.SCR_SETTINGS

		if self.status == 0:
			if key == 1:
				if self.threshold > 0: self.threshold -= 5
			elif key == 0:
				if self.threshold < 100: self.threshold += 5
			elif key == 3:
				master_cmd({"command":"write_config","name":"threshold","value":self.threshold});
				return constants.SCR_SETTINGS

		return constants.SCR_NONE