import machine
import utime

led_pin = machine.Pin(25, machine.Pin.OUT)

while True:
    led_pin.value(1) # turn led on
    utime.sleep(3)
    led_pin.value(0)
    utime.sleep(3)
    