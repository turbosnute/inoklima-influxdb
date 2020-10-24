while :
do
    #echo "--- Start Call API"
    python3 influxklima.py
    RET=$?
    sleep 60
done