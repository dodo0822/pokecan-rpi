import json

bin_height = -1
lift_height = -1

def load():
	global bin_height, lift_height
	try:
		with open("../config.json", "r") as cfg:
			data = cfg.read().replace("\n", "")
			obj = json.loads(data)
			bin_height = obj["bin_height"]
			lift_height = obj["lift_height"]

	except (OSError, ValueError, IOError) as e:
		print e
		pass

def save():
	global bin_height, lift_height
	try:
		with open("../config.json", "w") as cfg:
			data = json.dumps({ "bin_height": bin_height, "lift_height": lift_height })
			cfg.write(data)

	except (OSError, IOError) as e:
		pass
