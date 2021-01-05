import sys
import binascii
import struct
import time
from bluepy.btle import UUID, Peripheral

led_service_uuid ="0000180a-0000-1000-8000-00805f9b34fb"
led_char_uuid = "00002902-0000-1000-8000-00805f9b34fb"

if len(sys.argv) != 2:
    print("Fatal, must pass device address:", sys.argv[0], "<device address="">")
    quit()

p = Peripheral(sys.argv[1], "public")
LedService=p.getServiceByUUID(led_service_uuid)
print (LedService)

try:
    ch = LedService.getCharacteristics(led_char_uuid)[0]
    if (ch.supportsRead()):
        while 1:
            val = binascii.b2a_hex(ch.read())
            print ("0x" + val)
            time.sleep(1)

finally:
    p.disconnect()
