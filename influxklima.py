import serial
import json
import os

ser = serial.Serial('/dev/ttyACM2',115200)
ser.flushInput()

location = os.getenv('LOCATION', "Sluppen")

def is_json(myjson):
  try:
    json_object = json.loads(myjson)
  except ValueError as e:
    return False
  return True

while True:
    try:
        ser_bytes = ser.readline()
        decoded_bytes = ser_bytes[0:len(ser_bytes)-2].decode("utf-8")
        if is_json(decoded_bytes) is True:
            data = json.loads(decoded_bytes)
            temp = data['Temp']
            humidity = data['Humidity']
            pressure = data['Pressure']
            dewPoint = data['DewPoint']
            equivSeaLvlPressure = data['EquivSeaLvlPressure']
            rawH2 = data['RawH2']
            rawEthanol = data['RawEthanol']
            TVOC = data['TVOC']
            eCO2 = data['eCO2']
            light = data['eCO2']

            output = [
            {
                "measurement": "klima",
                "tags": {
                    "location": location
                },
                "fields": {
                     "Temperature": temp,
                     "Humidity": humidity,
                     "Pressure": pressure,
                     "dewPoint": dewPoint,
                     "SeaLevelPressure": equivSeaLvlPressure,
                     "H2": rawH2,
                     "Ethanol": rawEthanol,
                     "TVOC": TVOC,
                     "eCO2": eCO2,
                     "Light": light
                }
            }
            ]

            print(output)
    except:
        print("Keyboard Interrupt")
        break
