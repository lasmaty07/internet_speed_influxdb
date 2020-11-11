#!/usr/bin/python3
import datetime, logging ,json, os, time
import speedtest
from influxdb import InfluxDBClient

LOG_FILENAME = 'internetSpeed.log'
LOG_LEVEL=logging.ERROR

logging.basicConfig(filename=LOG_FILENAME,level=LOG_LEVEL)

try:
	with open('config.json', 'r') as f:
		config = json.load(f)
		logging.info('Config loaded ok')
except IOError as e:
	logging.error(e)


current_dir = os.path.dirname(os.path.abspath(__file__))

influxdb_host     = config["INFLUXDB_SERVER"]
influxdb_port     = config["INFLUXDB_PORT"]
influxdb_database = config["INFLUXDB_DATABASE"]


def persists(measurement, fields, time):
    logging.info("{} {} {}".format(time, measurement, fields))

    influx_client.write_points([{
        "measurement": measurement,
        "time": time,
        "fields": fields
    }])


influx_client = InfluxDBClient(host=influxdb_host, port=influxdb_port, database=influxdb_database)

def get_speed():
    logging.info("Calculating speed ...")
    s = speedtest.Speedtest()
    s.get_best_server()
    s.download()
    s.upload()

    return s.results.dict()

def test_speed():
    current_time = datetime.datetime.utcnow().isoformat()
    speed = get_speed()

    persists(measurement='internet', fields={"donwload": speed['download']}, time=current_time)
    persists(measurement='internet', fields={"upload": speed['upload']}, time=current_time)
    persists(measurement='internet', fields={"ping": speed['ping']}, time=current_time)
    logging.info('persisted to InfluxDB Ok')


try:
	test_speed ()
except Exception as e:
        logging.error(e)
