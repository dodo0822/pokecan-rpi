from PIL import Image

import constants
from fonts import font, font_status, font_time

class AboutScreen:
	def __init__(self):
		"init"

	def render(self, draw):
		draw.rectangle((0, 0, 128, 64), outline=0, fill=0)
		logo = Image.open("./images/pokecan.png")
		draw.bitmap((0, 0), logo, fill=255)
		draw.text((10, 45), "by Dodo, Pierre, Sasa", fill=255, font=font)

	def key(self, key):
		global scr
		if key == 2:
			return constants.SCR_MENU

		return constants.SCR_NONE