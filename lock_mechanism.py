import RPi.GPIO as GPIO
import time

photoPin = 14
servoLockPin = 15
#servoOpenPin = 18

servoMin = 3
servoMax = 12

def dutyCycle(degree):
    if degree > 180:
        degree = 180
    duty = servoMin + (degree*(servoMax-servoMin)/180.0)
    return duty

def servoMotor(pin, degree, t):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin, GPIO.OUT)
    p=GPIO.PWM(pin, 50)
    
    p.start(0)
    p.ChangeDutyCycle(dutyCycle(degree))
    time.sleep(t)
    
    p.stop()
    GPIO.cleanup(pin)

def lock(self):
    print (' Door locked!! ')
    servoMotor(servoLockPin, 180, 5)

def unlock(self):
    print (' Door unlocked!! ')
    servoMotor(servoLockPin, 0, 5)
    
GPIO.setmode(GPIO.BCM)
GPIO.setup(photoPin, GPIO.IN)
GPIO.add_event_detect(photoPin, GPIO.RISING, callback=lock, bouncetime=100)

