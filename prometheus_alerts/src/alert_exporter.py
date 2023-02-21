from prometheus_client import start_http_server, Gauge
import random
import time


def get_random_value():
    random_value_list = ['1', '2', '3', '4', '10', '20', '0']
    return random.choice(random_value_list)


prometheus_metric_value = Gauge('randome_value', 'Get randome value from list')


if __name__ == '__main__':
    start_http_server(9000)
    while True:
        prometheus_metric_value.set(get_random_value())
        time.sleep(60)
