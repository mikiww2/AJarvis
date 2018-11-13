
import base64, logging, os, json

class Configuration:
	def __init__(self, Logger, config_file='config/config.json', authAJarvis_file='config/authAJarvis.json'):
#get logger
		self.logger=Logger.set_logger(logging.getLogger(__name__))

		self.logger.debug('Start logger')
		self.logger.debug('Init configuration')
#### secrety key for encrypted sessions
		self._session_secret_key=base64.b64encode(os.urandom(24)).decode('utf-8') # 24 bytes or more ?
		self.logger.info('Generated random key for encrypting session : %s', self._session_secret_key) #utf-8 or default (bytes)?
#### load config ####
		if not os.path.isfile(config_file):
			self.logger.error(config_file + ' not found')

		with open(config_file, 'r') as file:
			config = json.load(file)

		if not config:
			self.logger.error('Cannot load %s', config_file)

		if not config['app'] or not config['app']['host'] or not config['app']['port']:
			self.logger.error('Cannot load %s app configuration', config_file)

		self._app_config=config['app']
		self._app_config['port']=int(self._app_config['port'])

		if not self._app_config['reloader'] or self._app_config['reloader'] != '0':
			self._app_config['reloader']=False
		else:
			self._app_config['reloader']=True

		self.logger.debug('app_config = %s', self._app_config)

#### load authAJarvis ####
		if not os.path.isfile(authAJarvis_file):
			self.logger.error(authAJarvis_file + ' not found')

		with open(authAJarvis_file, 'r') as file:
			authAJarvis = json.load(file)

		if not authAJarvis or not authAJarvis['path'] or not authAJarvis['username'] or not authAJarvis['password']:
			self.logger.error('authAJarvis not valid')
			self._pathAJarvis=None
			self._userAJarvis=None
			self._passAJarvis=None
		else:
			self._pathAJarvis=authAJarvis['path']
			self._userAJarvis=authAJarvis['username']
			self._passAJarvis=authAJarvis['password']
####
		self.logger.info('Load configuration without error')

#### retrieve methods ####
	def get_session_key(self):
		return self._session_secret_key

	def get_app_config(self):
		return self._app_config

	def get_path_AJarvis(self):
		return self._pathAJarvis

	def get_username_AJarvis(self):
		return self._userAJarvis

	def get_password_AJarvis(self):
		return self._passAJarvis



