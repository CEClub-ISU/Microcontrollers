import network
import ubinascii

# store specific logins on the pico itself, not GitHub
ssid = 'IASTATE'
password = ''

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

mac = ubinascii.hexlify(network.WLAN().config('mac'),':').decode()
print(mac)

while not wlan.isconnected():
    pass

print('Connected to network:', ssid)
print('Network config:', wlan.ifconfig())
