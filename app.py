from flask import Flask, render_template, request
from influxdb import InfluxDBClient
import grpc
from chirpstack_api import api

server = "" #add respective server IP address

#API Token generation is explained in document "Chirpstack", module:
api_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJjaGlycHN0YWNrIiwiaXNzIjoiY2hpcnBzdGFjayIsInN1YiI6IjczMjZlOTk3LWFiNmQtNDRlOS05NmI3LTE3ZDM3MTU0YmJkMiIsInR5cCI6ImtleSJ9.CFTrFLgpZUuFErdzRRRKu5UFLKdwi1xgBTGc000b_Mo"
app = Flask(__name__)

last_state = 0

# gRPC client initialization
channel = grpc.insecure_channel(server)
client = api.DeviceServiceStub(channel)
auth_token = [("authorization", "Bearer %s" % api_token)]


#Upon calling this URL, main() is called which renders main.html
@app.route('/')
def main():
    return render_template('main.html')

#Water meter latest values shown in device page
#Purpose: To retrieve values from "device_frmpayload_data_decoded_data" measurement for displaying device information in influx.html
#Note: This function queries the InfluxDB and returns the latest value, timestamp, device name, and device EUI. The influxQL query values are taken in as a list and later used in index.html using index function

def get_last_value():
    try:
        client = InfluxDBClient(host=' ', port=8086, database='water_meter')
        query = 'SELECT last("value") AS "value", time, dev_eui, device_name FROM device_frmpayload_data_decoded_data'
        result = client.query(query)
        #query values added to list
        points = list(result.get_points())
        if points:
            last_value = points[0]['value']
            last_time = points[0]['time']
            device_name = points[0]['device_name']
            device_eui = points[0]['dev_eui']
        else:
            last_value = None
            last_time = None
            device_name = None
            device_eui = None

        client.close()
        return last_value, last_time, device_name, device_eui
    #incase of any error "None" is given
    except Exception as e:
        print("Error retrieving data from InfluxDB:", e)
        return None, None, None, None
    
#water meter last 10 values
#Purpose: To retrieve last ten values from "device_frmpayload_data_decoded_data" measurement for displaying device the values in water.html
#Note: This function queries the InfluxDB and returns the last ten values of totalizer, battery, flow, and tamper status.
def get_last_10_values_table():
    try:
        client = InfluxDBClient(host=' ', port=8086, database='water_meter')

        # Query to retrieve the last 10 totalizer values
        query_totalizer = 'SELECT "value" FROM device_frmpayload_data_decoded_data ORDER BY time DESC LIMIT 10'
        result_totalizer = client.query(query_totalizer)
        totalizer_points = list(result_totalizer.get_points())

        # Query to retrieve the last 10 battery voltage values
        query_battery = 'SELECT "value" FROM device_frmpayload_data_byte18 ORDER BY time DESC LIMIT 10'
        result_battery = client.query(query_battery)
        battery_points = list(result_battery.get_points())

        # Query to retrieve the last 10 flow status values
        query_flow = 'SELECT "value" FROM device_frmpayload_data_byte16 ORDER BY time DESC LIMIT 10'
        result_flow = client.query(query_flow)
        flow_points = list(result_flow.get_points())

        # Query to retrieve the last 10 tamper status values
        query_tamper = 'SELECT "value" FROM device_frmpayload_data_byte14 ORDER BY time DESC LIMIT 10'
        result_tamper = client.query(query_tamper)
        tamper_points = list(result_tamper.get_points())

        # Combine the points into a list of dictionaries
        combined_points = []
        for i in range(10):
            combined_points.append({
                'totalizer': totalizer_points[i]['value'] if i < len(totalizer_points) else None,
                'battery': battery_points[i]['value'] if i < len(battery_points) else None,
                'flow': flow_points[i]['value'] if i < len(flow_points) else None,
                'tamper': tamper_points[i]['value'] if i < len(tamper_points) else None
            })

        client.close()

        return combined_points
    except Exception as e:
        print("Error retrieving data from InfluxDB:", e)
        return []
    

#Tempereature_sensor_last 10values
#Purpose: To retrieve last ten values from "device_frmpayload_data_data2" measurement, for displaying the values in Temp.html
#Note: This function queries the InfluxDB and returns the last ten values of temperature, humidity, ozone concentration, fast AQI, and EPA AQI.
def get_last_10_temp_values_table():
    try:
        client = InfluxDBClient(host=' ', port=8086, database='temp')

        query_temperature = 'SELECT "value" FROM device_frmpayload_data_data2 ORDER BY time DESC LIMIT 10'
        result_temperature = client.query(query_temperature)
        temperature_points = list(result_temperature.get_points())

        query_humidity = 'SELECT "value" FROM device_frmpayload_data_data3 ORDER BY time DESC LIMIT 10'
        result_humidity = client.query(query_humidity)
        humidity_points = list(result_humidity.get_points())

        query_ozone_concentration = 'SELECT "value" FROM device_frmpayload_data_data4 ORDER BY time DESC LIMIT 10'
        result_ozone_concentration = client.query(query_ozone_concentration)
        ozone_concentration_points = list(result_ozone_concentration.get_points())

        query_fast_aqi = 'SELECT "value" FROM device_frmpayload_data_data5 ORDER BY time DESC LIMIT 10'
        result_fast_aqi = client.query(query_fast_aqi)
        fast_aqi_points = list(result_fast_aqi.get_points())

        query_epa_aqi = 'SELECT "value" FROM device_frmpayload_data_data6 ORDER BY time DESC LIMIT 10'
        result_epa_aqi = client.query(query_epa_aqi)
        epa_aqi_points = list(result_epa_aqi.get_points())

        # Combine the points into a list of dictionaries
        combined_points = []
        for i in range(10):
            combined_points.append({
                'temperature': temperature_points[i]['value'] if i < len(temperature_points) else None,
                'humidity': humidity_points[i]['value'] if i < len(humidity_points) else None,
                'ozone_concentration': ozone_concentration_points[i]['value'] if i < len(ozone_concentration_points) else None,
                'fast_aqi': fast_aqi_points[i]['value'] if i < len(fast_aqi_points) else None,
                'epa_aqi': epa_aqi_points[i]['value'] if i < len(epa_aqi_points) else None
            })

        client.close()

        return combined_points
    except Exception as e:
        print("Error retrieving data from InfluxDB:", e)
        return []


#latest value of temperature sensor shown in devices page
#Purpose: To retrieve last value from "device_frmpayload_data_data2" measurement, for displaying the values in device_TS.html
#Note: This function queries the InfluxDB and returns the latest value, timestamp, device name, and device EUI for the temperature sensor.
def get_last_value_ts():
    try:
        client = InfluxDBClient(host=' ', port=8086, database='temp')
        query = 'SELECT last("value") AS "value", time, dev_eui, device_name FROM device_frmpayload_data_data2'
        result = client.query(query)
        points = list(result.get_points())
        if points:
            last_value_ts = points[0]['value']
            last_time_ts = points[0]['time']
            device_name_ts = points[0]['device_name']
            device_eui_ts = points[0]['dev_eui']
        else:
            last_value_ts = None
            last_time_ts = None
            device_name_ts = None
            device_eui_ts = None

        query2 = 'SELECT last("value") AS "value" FROM device_frmpayload_data_data3'
        result2 = client.query(query2)
        points2 = list(result2.get_points())
        if points2:
            last_value_ts2 = points2[0]['value']
        else:
            last_value_ts2 = None

        client.close()

        return last_value_ts, last_time_ts, device_name_ts, device_eui_ts, last_value_ts2
    except Exception as e:
        print("Error retrieving data from InfluxDB:", e)
        return None, None, None, None, None


#Latest values slc shown in devices page
#Purpose: To retrieve last value from "device_frmpayload_data_decoded_data_30" measurement, for displaying the values in device_slc.html
#Note: This function queries the InfluxDB and returns the latest value, timestamp, device name, and device EUI for the SLC
def get_last_value_slc():
    try:
        client = InfluxDBClient(host=' ', port=8086, database='SLC_DTDS')
        query = 'SELECT last("value") AS "value", time, dev_eui, device_name FROM device_frmpayload_data_decoded_data_30'
        result = client.query(query)
        points = list(result.get_points())
        if points:
            last_value_slc = points[0]['value']
            last_time_slc = points[0]['time']
            device_name_slc = points[0]['device_name']
            device_eui_slc = points[0]['dev_eui']
        else:
            last_value_slc = None
            last_time_slc = None
            device_name_slc = None
            device_eui_slc = None

        query2 = 'SELECT last("value") AS "value" FROM device_frmpayload_data_decoded_data_33'
        result2 = client.query(query2)
        points2 = list(result2.get_points())
        if points2:
            last_value_slc2 = points2[0]['value']
        else:
            last_value_slc2 = None

        client.close()
        return last_value_slc, last_time_slc, device_name_slc, device_eui_slc, last_value_slc2
    except Exception as e: 
        print("Error retrieving data from InfluxDB:", e)
        return None, None, None, None, None 

#last 10 values of SLC
#Purpose: To retrieve last ten values from "device_frmpayload_data_decoded_data_39" measurement, for displaying the values in Temp.html

def get_last_10_slc_dtds_values():
    try:
        client = InfluxDBClient(host=' ', port=8086, database='SLC_DTDS')

        # Queries to retrieve the last 10 values for each measurement
        query_frequency = 'SELECT "value" FROM device_frmpayload_data_decoded_data_39 ORDER BY time DESC LIMIT 10'
        result_frequency = client.query(query_frequency)
        frequency_points = list(result_frequency.get_points())

        query_energy = 'SELECT "value" FROM device_frmpayload_data_decoded_data_30 ORDER BY time DESC LIMIT 10'
        result_energy = client.query(query_energy)
        energy_points = list(result_energy.get_points()) 

        query_current = 'SELECT "value" FROM device_frmpayload_data_decoded_data_35 ORDER BY time DESC LIMIT 10'
        result_current = client.query(query_current)
        current_points = list(result_current.get_points())

        query_voltage = 'SELECT "value" FROM device_frmpayload_data_decoded_data_33 ORDER BY time DESC LIMIT 10'
        result_voltage = client.query(query_voltage)
        voltage_points = list(result_voltage.get_points())

        query_power_factor = 'SELECT "value" FROM device_frmpayload_data_decoded_data_40 ORDER BY time DESC LIMIT 10'
        result_power_factor = client.query(query_power_factor)
        power_factor_points = list(result_power_factor.get_points())

        # Combine the points into a list of dictionaries
        combined_points = []
        for i in range(10):
            combined_points.append({
                'frequency': frequency_points[i]['value'] if i < len(frequency_points) else None,
                'energy': energy_points[i]['value'] if i < len(energy_points) else None,
                'current': current_points[i]['value'] if i < len(current_points) else None,
                'voltage': voltage_points[i]['value'] if i < len(voltage_points) else None,
                'power_factor': power_factor_points[i]['value'] if i < len(power_factor_points) else None
            })

        client.close()

        return combined_points
    except Exception as e:
        print("Error retrieving data from InfluxDB:", e)
        return []

        
#Purpose: To utilise gRPC protocols to send downlink to device using a switch in index.html
#Note: This defines a route that handles both GET and POST methods. The URL calls show_slc_dtds() and index() functions
@app.route('/index', methods=['GET', 'POST'])
def show_slc_dtds():
    combined_points = get_last_10_slc_dtds_values()
    return render_template('index.html', combined_points=combined_points)

#At first last_state is give default value 0. Then a channel is created for communication is created. Based on the state value data is sent. 
def index():
    global last_state
    if request.method == 'POST':
        state = int(request.form.get('state', 0))
        if state != last_state:
            channel = grpc.insecure_channel(server)
            client = api.DeviceServiceStub(channel)
            auth_token = [("authorization", "Bearer %s" % api_token)]
            req = api.EnqueueDeviceQueueItemRequest()
            if state == 1:
                req.queue_item.data = bytes([0x01, 0x00])
            else:
                req.queue_item.data = bytes([0x00, 0x00])
            req.queue_item.confirmed = False
            req.queue_item.dev_eui = "57760a8d663d4a0c"
            req.queue_item.f_port = 1
            resp = client.Enqueue(req, metadata=auth_token)
            print("Downlink ID:", resp.id)
            last_state = state
            return "Downlink sent successfully!"
    return render_template('index.html')


#Purpose: Whenever HTTP request moves to a specific URL end point temp() function is called
@app.route('/temp')
def temp():
    # Call the function to get the last 10 temperature values in the form of list
    combined_points = get_last_10_temp_values_table()

    #This data is then sent to html page
    return render_template('Temp.html', combined_points=combined_points)


@app.route('/water')
def water():
    combined_points = get_last_10_values_table()
    return render_template('water.html', combined_points=combined_points)

@app.route('/device_ts')
def device_ts():
    last_value_ts, timestamp_ts, device_name_ts, device_eui_ts, last_value_ts2 = get_last_value_ts()
    return render_template('device_TS.html', 
                           last_value_ts=last_value_ts, 
                           timestamp_ts=timestamp_ts, 
                           device_name_ts=device_name_ts, 
                           device_eui_ts=device_eui_ts, 
                           last_value_ts2=last_value_ts2)


@app.route('/device_slc')
def device_slc():
    last_value_slc, timestamp_slc, device_name_slc, device_eui_slc, last_value_slc2 = get_last_value_slc()
    return render_template('device_slc.html', last_value_slc=last_value_slc, timestamp_slc=timestamp_slc, device_name_slc=device_name_slc, device_eui_slc=device_eui_slc, last_value_slc2=last_value_slc2)

@app.route('/region')
def region():
    return render_template('region.html')

@app.route('/region_TS')
def region_TS():
    return render_template('region_TS.html')

@app.route('/region_slc')
def region_slc():
    return render_template('region_slc.html')

@app.route('/influx')
def influx():
    last_value, timestamp, device_name, device_eui = get_last_value()
    return render_template('influx.html', last_value=last_value, timestamp=timestamp, device_name=device_name, device_eui=device_eui)

if __name__ == '__main__':
    app.run(debug=True)
