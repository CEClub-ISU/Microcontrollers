import machine
import time

analogInputPin = ADC(31)

DIODE_OFFSET_VOLTAGE = 1.21

while True:
    analogVal = ADC.read_u16(analogInputPin)
    
    sensor_voltage = (analogVal / 65535) * 3.3
    
    sensor_voltage = (sensor_voltage - DIODE_OFFSET_VOLTAGE) * 1000
    
    temperature = (sensor_voltage/10)
    
    time.sleep(1)
    
    print("Temperature = ", temperature, " degrees Celcius\n")