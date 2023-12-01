from flask import Flask, request, jsonify, render_template_string
from prometheus_flask_exporter import PrometheusMetrics
import random
import time

app = Flask(__name__)
metrics = PrometheusMetrics(app)

# Define metrics
cpu_usage = metrics.gauge('cpu_usage', 'CPU usage')
disk_usage = metrics.gauge('disk_usage', 'Disk usage')
ram_usage = metrics.gauge('ram_usage', 'RAM usage')

# Define the metrics values dictionary
metrics_values = {
    'cpu_usage': 0,
    'disk_usage': 0,
    'ram_usage': 0,
    'running': False
}


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
            return render_template_string(html_content, status='Running')
        elif action == 'end':
            # Decrease metrics to 0
            metrics_values['cpu_usage'] = 0
            metrics_values['disk_usage'] = 0
            metrics_values['ram_usage'] = 0
            metrics_values['running'] = False
            return render_template_string(html_content, status='Stopped')

    return render_template_string(html_content, status='')


@app.route('/metrics', methods=['GET'])
def get_metrics():
    return jsonify(metrics_values)


if __name__ == '__main__':
    app.run(debug=True, port=5555)
