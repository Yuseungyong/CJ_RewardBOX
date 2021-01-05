import RPi.GPIO as GPIO
import time

servoPin = 10
servoMax = 12
servoMin = 3

GPIO.setmode(GPIO.BOARD)
GPIO.setup(servoPin, GPIO.OUT)

servo = GPIO.PWM(servoPin, 50)
servo.start(0)

def setServoPos(degree):
    if degree > 180:
        degree = 180
    
    duty = servoMin + (degree*(servoMax-servoMin)/180.0)
    print("Degree: {}, Duty: {}".format(degree, duty))
    servo.ChangeDutyCycle(duty)

setServoPos(0)
time.sleep(1)
setServoPos(50)
time.sleep(1)
setServoPos(0)
time.sleep(1)

servo.stop()
GPIO.cleanup