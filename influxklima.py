from influxdb import InfluxDBClient
import serial
import json
import os
import datetime

location = os.getenv('LOCATION', "Sluppen")
devicepath = os.getenv('DEVICE_PATH', '/dev/ttyACM2')
influxhost=os.getenv('INFLUXDB_HOST', "influxdb")
influxport=os.getenv('INFLUXDB_PORT', 8086)
influxuser=os.getenv('INFLUXDB_USER', 'root')
influxpw=os.getenv('INFLUXDB_PW', 'root')
influxdb=os.getenv('INFLUXDB_DATABASE', 'inoklima')
debug=os.getenv('DEBUG', 'False')

def is_json(myjson):
  try:
    json_object = json.loads(myjson)
  except ValueError as e:
    return False
  return True

def is_HexDecNumeric(ser):
  try:
    int(ser,16)
  except ValueError as e:
    return False
  return True

def str2bool(v):
  return v.lower() in ("yes", "true", "t", "1")

if str2bool(debug):
    print("Influxdb Host: " + influxuser + "@" + influxhost + ":" + str(influxport))
    print("Influxdb Password: " + '*'*len(influxpw))
    print("Influxdb DB: " + influxdb)

ser = serial.Serial(devicepath, 115200)
ser.flushInput()
client = InfluxDBClient(influxhost, influxport, influxuser, influxpw, influxdb)

while True:
    try:
        ser_bytes = ser.readline()
        decoded_bytes = ser_bytes[0:len(ser_bytes)-2].decode("utf-8")
        if is_json(decoded_bytes) is True:
            data = json.loads(decoded_bytes)
            if "Temp" in data:
                # MEASUREMENT
                temp = data['Temp']
                humidity = data['Humidity']
                pressure = data['Pressure']
                dewPoint = data['DewPoint']
                equivSeaLvlPressure = data['EquivSeaLvlPressure']
                rawH2 = data['RawH2']
                rawEthanol = data['RawEthanol']
                TVOC = data['TVOC']
                eCO2 = data['eCO2']
                light = data['lux']
                
                influxdata = [
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
                client.write_points(influxdata)
            elif "ECO2BASE" in data:
                #{ "ECO2BASE": "8F2B", "TVOCBASE": "91BB" }
                # BASELINE CALIBRATION
                serialnum = data['Serial']
                eCO2_base = data['ECO2BASE']
                TVOC_base = data['TVOCBASE']

                influxdata = [
                {
                    "measurement": "sgp30_base",
                    "tags": {
                        "serial": serialnum
                    },
                    "fields": {
                        "eCO2_base": eCO2_base,
                        "TVOC_base": TVOC_base
                    }
                }
                ]
                if str2bool(debug):
                  print(influxdata)
                client.write_points(influxdata)
            elif "Request" in data:
              # Request for previous baseline.
              # Query InfluxDB.
              # Send reply.
              if str2bool(debug):
                print("request received.")
              influxdata = [{"nuthin": "null"}]
              serialnum = data['Serial']
              query = "SELECT * FROM sgp30_base WHERE serial='" + serialnum + "' ORDER BY DESC LIMIT 1;"
              res = client.query(query)
              if len(res) > 0:
                if str2bool(debug):
                  print("got baseline from influxdb")
                points = list(res.get_points())[0]
                savedTvoc = points['TVOC_base']
                savedEco2 = points['eCO2_base']
                response = "<" + savedEco2 + '|' + savedTvoc+ ">"
                if str2bool(debug):
                  print(response)
                ser.write(response.encode())
              else:
                if str2bool(debug):
                  print("no saved baselines")
                response = '<Null>'
                ser.write(response.encode())
            if str2bool(debug):
              print(influxdata)
    except:
        print("Interrupt")
        break