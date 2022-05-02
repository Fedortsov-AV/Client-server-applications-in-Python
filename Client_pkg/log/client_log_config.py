import logging
import os
import sys

dir = os.path.dirname(os.path.abspath(__file__))
file = os.path.join(dir, 'client.log')

client_log = logging.getLogger('client')

fmt = logging.Formatter("%(asctime)s %(levelname)s %(module)s - %(message)s", "%d.%m.%Y %H:%M:%S")
client_log.setLevel(logging.DEBUG)

rotation = logging.FileHandler(file, encoding='UTF-8')
rotation.setLevel(logging.DEBUG)
stream = logging.StreamHandler(sys.stdout)
stream.setLevel(logging.INFO)

rotation.setFormatter(fmt)
stream.setFormatter(fmt)

client_log.addHandler(rotation)
client_log.addHandler(stream)

if __name__ == '__main__':
    client_log.debug('This is a debug message')
    # client_log.info('This is an info message')
    # client_log.warning('This is a warning message')
    # client_log.error('This is an error message')
    # client_log.critical('This is a critical message')
    # client_log.info('Тестовый запуск логирования')
