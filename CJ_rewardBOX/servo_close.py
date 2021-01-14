import RPi.GPIO as GPIO
import time
import pigpio
pi = pigpio.pi() # Connect to local Pi.

pin_IR = 16
pin_servo_open = 20
pin_servo_lock = 21
pin_switch = 26

bpm_list = [0,0,0,0,0]
step_list = [0,0,0,0,0]

GPIO.setmode(GPIO.BCM)
GPIO.setup(pin_IR,GPIO.IN)
GPIO.setwarnings(False)
GPIO.setup(pin_switch, GPIO.IN, pull_up_down=GPIO.PUD_UP) 

IR_cnt = 0
switch_cnt = 0
lock_switch = 0

try:
   
    pi.set_servo_pulsewidth(pin_servo_lock, 1800)
    pi.set_servo_pulsewidth(pin_servo_open, 800)
    time.sleep(1)
except KeyboardInterrupt:
    # switch servo off
    pi.set_servo_pulsewidth(pin_servo_lock, 0)
    pi.set_servo_pulsewidth(pin_servo_open, 0)
    pi.stop()

GPIO.cleanup