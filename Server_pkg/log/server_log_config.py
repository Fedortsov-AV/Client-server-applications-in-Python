import logging
import logging.handlers as hand
import os
import sys

dir = os.path.dirname(os.path.abspath(__file__))
file = os.path.join(dir, 'server.log')
fmt = logging.Formatter("%(asctime)s %(levelname)s %(module)s - %(message)s", "%d.%m.%Y %H:%M:%S")

rotation = hand.TimedRotatingFileHandler(file, when="D", interval=1, encoding='UTF-8', delay=True)
rotation.setLevel(logging.DEBUG)
stream = logging.StreamHandler(sys.stdout)
stream.setLevel(logging.INFO)

rotation.setFormatter(fmt)
stream.setFormatter(fmt)

server_log = logging.getLogger('server')
server_log.setLevel(logging.DEBUG)

server_log.addHandler(rotation)
server_log.addHandler(stream)

# for key in logging.Logger.manager.loggerDict:
#     print(key)
#
# print(server_log)
# print(server_log.level)
# print(server_log.handlers)


if __name__ == '__main__':
    server_log.debug('This is a debug message')
    # server_log.info('This is an info message')
    # server_log.warning('This is a warning message')
    # server_log.error('This is an error message')
    # server_log.critical('This is a critical message')
    # server_log.info('Тестовый запуск логирования')
