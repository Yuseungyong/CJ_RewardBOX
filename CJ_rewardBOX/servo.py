import RPi.GPIO as GPIO
import time
import pigpio
pi = pigpio.pi() # Connect to local Pi.

pin_IR = 16
pin_servo_open = 20
pin_servo_lock = 21
pin_switch = 26

GPIO.setmode(GPIO.BCM)
GPIO.setup(pin_IR,GPIO.IN)
GPIO.setwarnings(False)
GPIO.setup(pin_switch, GPIO.IN, pull_up_down=GPIO.PUD_UP) 


servo = int(input("open : 1, close : 0\n"))
pi.set_servo_pulsewidth(pin_servo_open, 800)

if servo == 0:
    pi.set_servo_pulsewidth(pin_servo_lock, 1800)
else:
    pi.set_servo_pulsewidth(pin_servo_lock, 800)
time.sleep(1)


GPIO.cleanup