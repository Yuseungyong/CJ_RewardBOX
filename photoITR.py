import RPi.GPIO as GPIO
import time

photoPin = 16

def lock(chn):
    
    if GPIO.input(photoPin) == 1:
        print (' BOX LOCKED!! {}'.format(GPIO.input(photoPin)))
    
    

GPIO.setmode(GPIO.BOARD)
GPIO.setup(photoPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(photoPin, GPIO.FALLING, callback=lock, bouncetime=500)

