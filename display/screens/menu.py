import constants
from fonts import font, font_status, font_time

class MenuScreen():
	menu_items = ["Settings", "Network", "About"]

	def __init__(self):
		self.selected = 0
		self.scroll_top = 0
		self.scroll_bot = 4 if len(self.menu_items) > 4 else len(self.menu_items)

	def render(self, draw):
		draw.rectangle((0, 0, 128, 64), outline=0, fill=0)
		draw.text((0, 0), "Pokecan Menu", fill=255, font=font_status)
		for i in range(self.scroll_top, self.scroll_bot):
			if self.selected == i:
				line = "> "
			else:
				line = "   "

			line += self.menu_items[i]
			draw.text((0, 16+((i-self.scroll_top)*12)), line, fill=255, font=font)
			
	def key(self, key):
		if key == 2:
			return constants.SCR_MAIN
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
				return constants.SCR_SETTINGS
			elif self.selected == 1:
				return constants.SCR_NETWORK
			elif self.selected == 2:
				return constants.SCR_ABOUT

		return constants.SCR_NONE