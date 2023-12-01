from flask import Flask, request, jsonify, render_template_string
from prometheus_flask_exporter import PrometheusMetrics
import random
import time
import logging
import logstash

# Configure logging to send logs to Logstash
logger = logging.getLogger('my_logger')
logger.setLevel(logging.INFO)
logger.addHandler(logstash.LogstashHandler('localhost', 5000))

app = Flask(__name__)
metrics = PrometheusMetrics(app)

# Define metrics
cpu_usage = metrics.gauge('cpu_usage', 'CPU usage')
disk_usage = metrics.gauge('disk_usage', 'Disk usage')
ram_usage = metrics.gauge('ram_usage', 'RAM usage')

initial_disk = random.randint(10, 40)
initial_cpu = random.randint(20, 35)
initial_ram = random.randint(30, 50)

# Define the metrics values dictionary
metrics_values = {
    'cpu_usage': initial_cpu,
    'disk_usage': initial_disk,
    'ram_usage': initial_ram,
    'running': False
}

# Define the log entry templates
log_entry_templates = [
    "CPU load is high: {{ cpu_usage }}%",
    "Disk usage is high: {{ disk_usage }}%",
    "RAM usage is high: {{ ram_usage }}%",
    "Critical error detected!"
]


def log_entry(log_message):
    # Generate a log entry with the provided message
    logger.info(log_message)


@app.route('/', methods=['GET', 'POST'])
def index():
    # The HTML content is directly embedded in the script.
    html_content = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Metrics Simulation</title>
    </head>
    <body>
        <h1>Metrics Simulation</h1>
        <h2>Status: {{ status }}</h2>
        <form method="post">
            <input type="submit" name="action" value="start">
            <input type="submit" name="action" value="end">
        </form>
    </body>
    </html>
    '''

    if request.method == 'POST':
        action = request.form['action']
        if action == 'start':
            # Increase metrics to random values between 80 and 100%
            metrics_values['cpu_usage'] = random.randint(80, 100)
            metrics_values['disk_usage'] = random.randint(80, 100)
            metrics_values['ram_usage'] = random.randint(80, 100)
            metrics_values['running'] = True

            # Log the initial state of the application
            log_entry("Application started with CPU: {}%, Disk: {}%, RAM: {}%".format(
                metrics_values['cpu_usage'], metrics_values['disk_usage'], metrics_values['ram_usage']))

            return render_template_string(html_content, status='Running')
        elif action == 'end':
            # Decrease metrics to default values
            metrics_values['cpu_usage'] = initial_cpu
            metrics_values['disk_usage'] = initial_disk
            metrics_values['ram_usage'] = initial_ram
            metrics_values['running'] = False

            # Log the end of the test
            log_entry("Application test ended. Metrics reset to default values.")

            return render_template_string(html_content, status='Stopped')

    return render_template_string(html_content, status='')


@app.route('/metrics', methods=['GET'])
def get_metrics():
    return jsonify(metrics_values)


if __name__ == '__main__':
    app.run(debug=True, port=5555)
