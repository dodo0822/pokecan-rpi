import Adafruit_PCA9685

pca = Adafruit_PCA9685.PCA9685()
pca.set_pwm_freq(500)

pca.set_pwm(6, 0, 4095)
pca.set_pwm(7, 0, 4095)
pca.set_pwm(12, 0, 0)
pca.set_pwm(13, 0, 4095)
pca.set_pwm(14, 0, 0)
pca.set_pwm(15, 0, 4095)

try:
	input("Press enter to stop")
except SyntaxError:
	pass

pca.set_pwm(6, 0, 0)
pca.set_pwm(7, 0, 0)
pca.set_pwm(12, 0, 0)
pca.set_pwm(13, 0, 0)
pca.set_pwm(14, 0, 0)
pca.set_pwm(15, 0, 0)