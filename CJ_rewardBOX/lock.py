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

def main():

    #change this value
    open_bpm_cnt = 10
    open_bpm = 100
    open_step = 200


    #init_value
    bpm_list = []
    for i in range(5):
        bpm_list.append(0)


    IR_cnt = 0
    switch_cnt = 0
    lock_switch = 0
    data1_before = 0
    data2_before = 0
    data3_before = 0
    data4_before = 0
    bpm_cnt = 0
    step = 0

    file4 = open("mode.txt", 'w')
    file4.write("None")
    mode = "None"
    file_bpm = open("bpm_cnt.txt", 'w')
    file_bpm.write("0")
    file_bpm_off = open("bpm_cnt_off.txt", 'w')
    file_bpm_off.write("0")
    
    
    #open_init
    #servo
    pi.set_servo_pulsewidth(pin_servo_open, 800)
    pi.set_servo_pulsewidth(pin_servo_lock, 800)
    time.sleep(1)


    while True:
        #read txt files in 0.5sec
        time.sleep(0.5) 

        file1 = open("BPM_output.txt", 'r')
        data1 = file1.read()
        file2 = open("STEP_output.txt", 'r')
        data2 = file2.read()
        file3 = open("STEP_offset.txt", 'r')
        data3 = file3.read()
        file4 = open("mode.txt", 'r')
        mode = file4.read()

        #blank error in txt file
        if data1 =="":
            data1 = data1_before
        if data2 =="":
            data2 = data2_before
        if data3 =="":
            data3 = data3_before  
        data1_before = data1
        data2_before = data2
        data3_before = data3 
        
        bpm = int(data1)
        step = int(data2) - int(data3) #step - offset
        
        bpm_list.pop(0)
        bpm_list.append(bpm)

        AVG_bpm = sum(bpm_list)/len(bpm_list)

        #init_bpm_cnt
        file_bpm = open("bpm_cnt.txt", 'w')
        file_bpm.write(str(bpm_cnt))
        file_bpm_off = open("bpm_cnt_off.txt", 'r')
        data4 = file_bpm_off.read()
        try:
            if data4 != "0":
                if AVG_bpm >= open_bpm and mode == "bpm":
                    bpm_cnt -= int(data4) + 3
                else:
                    bpm_cnt -= int(data4)
                print(data4)
                file_bpm_off = open("bpm_cnt_off.txt", 'w')
                file_bpm_off.write("0")
        except:
            pass    
            
        if AVG_bpm >= open_bpm and mode == "bpm":
            bpm_cnt +=1      


        #lock
        if lock_switch == 0:
            #IR detected
            if GPIO.input(pin_IR) == 1:
                IR_cnt += 1
            
            #servo
            if IR_cnt >= 2:
                print("lock", IR_cnt)

                pi.set_servo_pulsewidth(pin_servo_lock, 1800)
                pi.set_servo_pulsewidth(pin_servo_open, 800)
                time.sleep(1)

                lock_switch = 1
                IR_cnt = 0

        #open
        elif lock_switch == 1:
            
            if bpm_cnt >= open_bpm_cnt and mode == "bpm" or step >= open_step and mode == "step":
                print("open", switch_cnt)

                pi.set_servo_pulsewidth(pin_servo_lock, 800)
                time.sleep(0.5)

                pi.set_servo_pulsewidth(pin_servo_open, 1800)
                time.sleep(0.5)

                pi.set_servo_pulsewidth(pin_servo_open, 800)
                time.sleep(0.5)

                lock_switch = 0

        print("IR_cnt :",IR_cnt, "lock_switch :", lock_switch, "AVG_bpm :",AVG_bpm, "step :",step, 
        "bpm_cnt :",bpm_cnt, "mode :", mode)


    GPIO.cleanup
