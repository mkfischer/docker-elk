from flask import Flask, Response
from prometheus_client import Gauge, generate_latest
import time
import threading
import json
import socket

app = Flask(__name__)

# Define Prometheus metrics
g_cpu = Gauge('cpu_usage', 'CPU usage', ['core'])
g_hdd = Gauge('hdd_usage', 'HDD usage', ['drive'])
g_memory = Gauge('memory_usage', 'Memory usage')
g_http = Gauge('http_load', 'HTTP server load')
g_db = Gauge('db_load', 'Database server load')

# Initialize metrics
for i in range(4):
    g_cpu.labels(core=f'core{i}').set(10)
g_hdd.labels(drive='drive0').set(10)
g_memory.set(10)
g_http.set(10)
g_db.set(10)

LOGSTASH_HOST = 'logstash'  # Replace with your Logstash host
LOGSTASH_PORT = 50000


def send_to_logstash():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((LOGSTASH_HOST, LOGSTASH_PORT))

    while True:
        data = {
            "cpu_usage": [g_cpu.labels(core=f'core{i}')._value.get() for i in range(4)],
            "hdd_usage": g_hdd.labels(drive='drive0')._value.get(),
            "memory_usage": g_memory._value.get(),
            "http_load": g_http._value.get(),
            "db_load": g_db._value.get()
        }
        message = json.dumps(data) + "\n"  # JSON Lines format
        client_socket.sendall(message.encode('utf-8'))
        time.sleep(15)  # Adjust the sleep time as needed


def increase_load():
    load_value = 10
    while load_value <= 110:
        for i in range(4):
            g_cpu.labels(core=f'core{i}').set(load_value)
        g_hdd.labels(drive='drive0').set(load_value)
        g_memory.set(load_value)
        g_http.set(load_value)
        g_db.set(load_value)

        load_value += 2
        time.sleep(6)


# Start the load increase and Logstash sending in separate threads
threading.Thread(target=increase_load).start()
threading.Thread(target=send_to_logstash).start()


@app.route('/metrics')
def metrics():
    return Response(generate_latest(), mimetype='text/plain')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9123)
