# inoklima-influxdb
Takes data from [inoklima](https://github.com/turbosnute/inoklima) and sends it to influxdb.

## Run
First create a database in your already running influxdb container:
```
sudo docker exec -it influxdb influx
> CREATE DATABASE inoklima
> exit
```

Then start the inoklima-influxdb container:
```
sudo docker run -d --device=/dev/ttyACM2 \
 -e LOCATION='Lilby' \
 -e DEVICE_PATH='/dev/ttyACM2' \
 -e INFLUXDB_HOST='nerd' \
 --restart unless-stopped \
 --name inoklima \
 turbosnute/inoklima-influxdb
```

## Environment vars

- LOCATION ['Sluppen']
- DEVICE_PATH ['/dev/ttyACM2']
- INFLUXDB_HOST ['influxdb']
- INFLUXDB_PORT [8086]
- INFLUXDB_USER ['root']
- INFLUXDB_PW ['root']
- INFLUXDB_DATABASE ['inoklima']
- DEBUG ['False']