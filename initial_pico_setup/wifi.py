import network

ssid = 'ICS 23 Twenty'
# specific to the Pico Matt and Sam were working on as of 4/5/23, registered under Matt's wifi account
password = 'bzYqqdBD'

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

while not wlan.isconnected():
    pass

print('Connected to network:', ssid)
print('Network config:', wlan.ifconfig())