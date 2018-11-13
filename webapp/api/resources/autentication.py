
import hashlib, logging, json

#provide autentication methods
class Autentication:
	def __init__(self, Logger, config_file='config/auth.json'):
#get logger
		self.logger=Logger.set_logger(logging.getLogger(__name__))

		self.logger.info('Start logger')
		self.logger.debug('Init configuration')

		with open(config_file, 'r') as file:
			auth_file=json.load(file)

		self.logger.debug('%s = %s', config_file, auth_file)

		if not auth_file or not auth_file['app_users']:
			self.logger.error('Cannot load %s', config_file)

		for user in auth_file['app_users']:
			user['hash_password']=self._hash(user['password'])

		self._app_users=auth_file['app_users']

		self.logger.info('Load authorized users')
		self.logger.debug('Authorized users = %s', self._app_users)

#### PRIVATE METHODS ####
	@staticmethod
	def _hash(password):
		return hashlib.sha224(password.encode('utf-8')).hexdigest()

#### PUBLIC METHODS ####
	def autenticate(self, username, password):
		hash_password=Autentication._hash(password)

		for user in self._app_users:
			self.logger.debug(user['username']+' == '+username+', '+user['hash_password']+' == '+hash_password)
			if user['username'] == username and user['hash_password'] == hash_password:
				return True
		return False