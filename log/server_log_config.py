import logging
import logging.handlers as hand

server_log = logging.getLogger('server')
server_log.setLevel(logging.DEBUG)

fmt = logging.Formatter("%(asctime)s %(levelname)s %(module)s - %(message)s", "%d.%m.%Y %H:%M:%S")

rotation = hand.TimedRotatingFileHandler("server.log.", when="M", interval=1, encoding='UTF-8', delay=False)
rotation.setFormatter(fmt)
server_log.addHandler(rotation)

stream = logging.StreamHandler()
stream.setFormatter(fmt)
server_log.addHandler(stream)
