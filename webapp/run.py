#from flask_sslify import SSLify

import logging

from api.app import App
from api.resources.logger import Logger


Logger=Logger()

logger=Logger.set_logger(logging.getLogger(__name__))
logger.info('Start logger')

App=App(Logger)
app, config=App.create_app()


#### app ####
if __name__ == "__main__":
	context = ('cert.crt', 'key.key')
	app.run(host=config['host'], port=config['port'], ssl_context=context, debug=__debug__, use_reloader=config['reloader']) # use_reloader=True is default
	#sslify=SSLify(app, permanent=True) #redirect http to https, if __debug__ than disable