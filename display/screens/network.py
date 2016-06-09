import netifaces

import constants
from fonts import font, font_status, font_time

class NetworkScreen:
	devs = ["eth0", "wlan0"]
	texts = ["Wired", "Wireless"]
	def __init__(self):
		"init"
		self.link = [False, False]
		self.address = ["", ""]
		for i in range(0, 2):
			addr = netifaces.ifaddresses(self.devs[i])
			if netifaces.AF_INET in addr:
				self.link[i] = True
				self.address[i] = addr[netifaces.AF_INET][0]["addr"]
			else:
				self.link[i] = False
				self.address[i] = ""

	def render(self, draw):
		draw.rectangle((0, 0, 128, 64), outline=0, fill=0)
		draw.text((0, 0), "Network Status", fill=255, font=font_status)
		for i in range(0, 2):
			if self.link[i]:
				draw.text((0, (i*24) + 16), self.texts[i] + ": connected", fill=255, font=font)
				draw.text((0, (i*24) + 28), "IP: " + self.address[i], fill=255, font=font_time)
			else:
				draw.text((0, (i*24) + 16), self.texts[i] + ": disconnected", fill=255, font=font)

	def key(self, key):
		global scr
		if key == 2:
			return constants.SCR_MENU

		return constants.SCR_NONE