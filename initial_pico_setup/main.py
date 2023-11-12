# import statements
import utime
import machine
from time import sleep
import urequests
import json
import network
import ubinascii
import dht
import gc
gc.enable()
# hardware setup
# pin declarations
tempSensor = machine.ADC(0)

lightSensor = machine.ADC(machine.Pin(27))

humiditySensor = dht.DHT11(machine.Pin(4))

pwm = machine.PWM(machine.Pin(2))	# PWM clock for use with voltage doubler
pwm.freq(1000)      # Set the frequency value        
pwm.duty_u16(32767)     # Set the duty cycle to 65535/2 to emulate a clock

wifiIndicator = machine.Pin(16, machine.Pin.OUT)
wifiIndicator.value(0)

# temp sensor read function
def readTemp():
    rawVal = 0
    for i in range(20):    # basic averaging loop
        rawVal += tempSensor.read_u16()
    rawVal /= 20
    
    sensorVoltage = (rawVal / 65535 * 3.3) * 1000 #converting ADC value to voltage
    tempC = sensorVoltage / 10 # converting voltage to celsius
    tempF = tempC * (9 / 5) + 32 # converting celsius to fahrenheit
    return tempF

# light sensor read function
def readLight():
    rawVal = 0
    for i in range(20):  # basic averaging loop
        rawVal += lightSensor.read_u16()
    rawVal /= 20
    return rawVal

# humidity sensor read function
def readHumidity():
    humiditySensor.measure()
    return humiditySensor.humidity()

# declare standard alert interval
isHour = False

# declare Air Temperature variables
currAirTemp = -1
maxAirTemp = 80.0
minAirTemp = 70.0

# declare Humidity variables
currHum = -1
maxHum = 60.0
minHum = 40.0

# declare PH variables
currPH = -1
maxPH = 6.4
minPH = 5.6

# declare Electric Conductivity variables
currElecCond = -1
maxElecCond = 1600
minElecCond = 1000

# declare Water Temperature variables
currWaterTemp = -1
maxWaterTemp = 72.0
minWaterTemp = 63.0

#declare Light Level variables
currLight = -1
currLightInd = "Good"
minLight = -1

#declare Entry Notice variable
entryNotice = 0
entryNoticeInd = 0

# Discord webhook setup
discordUrl = "https://discord.com/api/webhooks/1151599605562212383/0W0Eq4UDqSzl8pFzSc9SXUBRrkPAdTtijETcmweGmEs4hrHOmBm8HFwZR0uhXFkDA51F"
discordHeaders = {
    'Content-Type': 'application/json'
}

# Google Forms setup
formsUrl = "https://docs.google.com/forms/u/0/d/e/1FAIpQLSc9sOZXXNuvpBrPZ68fkTmNUmd6GxRRtQcM2YJ9qmGWYtZNAw/formResponse"
formsHeaders = {
    'Content-Type': 'application/x-www-form-urlencoded'
}

# sets real time clock
rtc = machine.RTC()
# (year, month, day, weekday, hours, minutes, seconds, subseconds)
rtc.datetime((2023, 4, 5, 4, 17, 14, 45, 0))

# ensures instant reading on plugin
justPluggedIn = True

# sets up wifi connection
wlan = network.WLAN(network.STA_IF)
# store logins on the pico itself, not GitHub
ssid = 'IASTATE'
password = ''
def wifiSetup():
    global wlan
    wlan.active(True)
    wlan.connect(ssid, password)

    mac = ubinascii.hexlify(network.WLAN().config('mac'),':').decode()
    print(mac)

    while not wlan.isconnected():
        pass
    wifiIndicator.value(1)
    print('Connected to network:', ssid)
    print('Network config:', wlan.ifconfig())
    gc.collect()

# gets current values formatted for Discord
def getData():
    embeds = [{"type": "rich","title": "Current Readings","fields": [{"name": "Air Temperature","value": str(currAirTemp) + " F","inline": "true"},{"name": "Humidity","value": str(currHum) + " %","inline": "true"},{"name": "PH","value": str(currPH),"inline": "true"},{"name": "Electric Conductivity","value": str(currElecCond) + " uS/cm","inline": "true"},{"name": "Water Temperature","value": str(currWaterTemp) + " F","inline": "true"},{"name": "Light Level","value": str(currLight),"inline": "true"},{"name": "Entry Notice","value": entryNoticeInd,"inline": "true"}]}]
    return embeds

# gets expected values formatted for Discord
def getExpected():
    embeds = [{"type": "rich","title": "Expected Readings","fields": [{"name": "Air Temperature","value": str(minAirTemp) + "-" + str(maxAirTemp) + " F","inline": "true"},{"name": "Humidity","value": str(minHum) + "-" + str(maxHum) + " %","inline": "true"},{"name": "PH","value": str(minPH) + "-" + str(maxPH),"inline": "true"},{"name": "Electric Conductivity","value": str(minElecCond) + "-" + str(maxElecCond) + " uS/cm","inline": "true"},{"name": "Water Temperature","value": str(minWaterTemp) + "-" + str(maxWaterTemp) + " F","inline": "true"},{"name": "Light Level","value": "Good","inline": "true"},{"name": "Entry Notice","value": "No Entry Detected","inline": "true"}]}]
    return embeds

# gets current values formatted for Google Forms
def getCurrentFormatted():
    # store logins on the pico itself, not GitHub
    formsPassword = "23472398478197498179871287489743897239840701724038917234089712903487210983470217409821347098"
    payload = "entry.906379933=" + str(currAirTemp) + "&entry.999512421=" + str(currHum) + "&entry.561794673=" + str(currPH) + "&entry.376241976=" + str(currElecCond) + "&entry.160733437=" + str(currWaterTemp) + "&entry.48490048=" + str(currLight) + "&entry.573586168=" + str(entryNoticeInd) + "&entry.270098587=" + str(formsPassword)
    return payload

# this function is the main body of the alert system, checks varaible values and alerts when needed
def checkVariables():
    alertMessages = []
    global currAirTemp
    global currLight
    global currHum
    # run variable read functions
    currAirTemp = readTemp()
    currLight = readLight()
    currHum = readHumidity()
    
    print(currAirTemp)
    print(currLight)
    print(currHum)
    
    # check readings against expected values
    # commenting out checks for which we don't yet have sensors
    if (currAirTemp > maxAirTemp):
        alertMessages.append("Air Temperature is Too High")
    if (currAirTemp < minAirTemp):
        alertMessages.append("Air Temperature is Too Low")
    if (currHum > maxHum):
        alertMessages.append("Humidity is Too High")
    if (currHum < minHum):
        alertMessages.append("Humidity is Too Low")
    if (currPH > maxPH):
        alertMessages.append("PH is Too High")
    if (currPH < minPH):
        alertMessages.append("PH is Too Low")
    if (currElecCond > maxElecCond):
        alertMessages.append("Electric Conductivity is Too High")
    if (currElecCond < minElecCond):
        alertMessages.append("Electric Conductivity is Too Low")
    if (currWaterTemp > maxWaterTemp):
        alertMessages.append("Water Temperature is Too High")
    if (currWaterTemp < minWaterTemp):
        alertMessages.append("Water Temperature is Too Low")
    if (currLight < 60000):
        alertMessages.append("Light Level is Too Low")
        currLightInd = "Low"
    if (entryNotice != 0):
        alertMessages.append("Entry Notice")
        entryNoticeInd = "Entry Detected"
    # alert on the hour if system is stable
    if (len(alertMessages) == 0):	#temporarily removed isHour check
        payload = json.dumps({
          "content": "System Readings Stable",
          "embeds": getData()
        })
        response = urequests.request("POST", discordUrl, headers=discordHeaders, data=payload)
        formsData = getCurrentFormatted();
        google = urequests.request("POST", formsUrl, headers=formsHeaders, data=formsData)
    # alert if any value is not expected
    if (len(alertMessages) != 0):
        alertsOutput = "URGENT: "
        for i in range(len(alertMessages)):
            alertsOutput = alertsOutput + alertMessages[i]
            if ((i+1) < len(alertMessages)):
                alertsOutput = alertsOutput + ", "
        payload = json.dumps({
          "content": alertsOutput,
          "embeds": getData()
        })
        response = urequests.request("POST", discordUrl, headers=discordHeaders, data=payload)
        formsData = getCurrentFormatted();
        google = urequests.request("POST", formsUrl, headers=formsHeaders, data=formsData)
        # output expected values
        payload = json.dumps({
          "embeds": getExpected()
        })
        response = urequests.request("POST", discordUrl, headers=discordHeaders, data=payload)
    alertMessages = []
    print("before: ", gc.mem_free())
    response.close()
    google.close()
    gc.collect()
    print(gc.mem_free())

# start of main
wifiSetup()

    
while True:
    # syncs program to 15 minute clock
#    while rtc.datetime()[5] not in {0, 15, 30, 45}: temporarily commented out
#        sleep(1)
#    if (rtc.datetime()[5] == 0):
#        isHour = True
#    else:
#        isHour = False
    # take current readings
#     currAirTemp = readAirTemp()
    # execute monitoring system
#    justPluggedIn = False
    if not wlan.isconnected:
        wifiIndicator.value(0)
        wifiSetup()
        wifiIndicator.value(1)
    checkVariables()
    gc.collect()
    # waits 15 minutes
    sleep(10)