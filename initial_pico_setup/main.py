# import statements
import utime
import machine
from time import sleep
import urequests
import json
import network
import ubinascii

# hardware setup
# pin declarations
# tempSensor = machine.ADC(0)

# temp sensor read function
# def readTemp():
#     rawVal = tempSensor.read_u16()
#     sensorVoltage = (rawVal / 65535 * 3.3) * 1000
#     tempC = sensorVoltage / 10
#     tempF = tempC * (9 / 5) + 32
#     return tempF

# declare standard alert interval
isHour = 0

# declare Air Temperature variables
currAirTemp = -1
maxAirTemp = 68.0
minAirTemp = 64.0

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
currLightInd = "No Data"
minLight = -1

#declare Entry Notice variable
entryNotice = 0
entryNoticeInd = "No Entry Detected"

# Discord webhook setup
url = "https://discord.com/api/webhooks/1151599605562212383/0W0Eq4UDqSzl8pFzSc9SXUBRrkPAdTtijETcmweGmEs4hrHOmBm8HFwZR0uhXFkDA51F"
headers = {
    'Content-Type': 'application/json'
}

# sets real time clock
rtc = machine.RTC()
# (year, month, day, weekday, hours, minutes, seconds, subseconds)
rtc.datetime((2023, 4, 5, 4, 17, 14, 45, 0))

# sets up wifi connection
def wifiSetup():
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

# gets current values
def getData():
    embeds = [{"type": "rich","title": "Current Readings","fields": [{"name": "Air Temperature","value": str(currAirTemp) + " F","inline": "true"},{"name": "Humidity","value": str(currHum) + " %","inline": "true"},{"name": "PH","value": str(currPH),"inline": "true"},{"name": "Electric Conductivity","value": str(currElecCond) + " uS/cm","inline": "true"},{"name": "Water Temperature","value": str(currWaterTemp) + " F","inline": "true"},{"name": "Light Level","value": currLightInd,"inline": "true"},{"name": "Entry Notice","value": entryNoticeInd,"inline": "true"}]}]
    return embeds

# gets expected values
def getExpected():
    embeds = [{"type": "rich","title": "Expected Readings","fields": [{"name": "Air Temperature","value": str(minAirTemp) + "-" + str(maxAirTemp) + " F","inline": "true"},{"name": "Humidity","value": str(minHum) + "-" + str(maxHum) + " %","inline": "true"},{"name": "PH","value": str(minPH) + "-" + str(maxPH),"inline": "true"},{"name": "Electric Conductivity","value": str(minElecCond) + "-" + str(maxElecCond) + " uS/cm","inline": "true"},{"name": "Water Temperature","value": str(minWaterTemp) + "-" + str(maxWaterTemp) + " F","inline": "true"},{"name": "Light Level","value": "Good","inline": "true"},{"name": "Entry Notice","value": "No Entry Detected","inline": "true"}]}]
    return embeds

# this function is the main body of the alert system, checks varaible values and alerts when needed
def checkVariables():
    alertMessages = []
    # check readings against expected values
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
    if (currLight < minLight):
        alertMessages.append("Light Level is Too Low")
        currLightInd = "Low"
    if (entryNotice != 0):
        alertMessages.append("Entry Notice")
        entryNoticeInd = "Entry Detected"
    # alert on the hour if system is stable
    if (isHour == 1 and len(alertMessages) == 0):
        payload = json.dumps({
          "content": "System Readings Stable",
          "embeds": getData()
        })
        response = urequests.request("POST", url, headers=headers, data=payload)
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
        response = urequests.request("POST", url, headers=headers, data=payload)
        # output expected values
        payload = json.dumps({
          "embeds": getExpected()
        })
        response = urequests.request("POST", url, headers=headers, data=payload)
    alertMessages = []

# start of main
wifiSetup()
# syncs program to 15 minute clock
while rtc.datetime()[5] not in {0, 15, 30, 45}:
    sleep(1)
    
while True:
    if (rtc.datetime()[5] == 0):
        isHour = 1
    else:
        isHour = 0
    # take current readings
#     currAirTemp = readAirTemp()
    # execute monitoring system
    checkVariables()
    # waits 15 minutes
    sleep(60*15)

