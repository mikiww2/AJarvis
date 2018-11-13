#!/usr/bin/env python3

import logging, requests, json #use of requests for connecting to AJarvis

class DownloadStandup:
	def __init__(self, Logger, config):
#get logger
		self.logger=Logger.set_logger(logging.getLogger(__name__))
		self.logger.info('start logger')

		self.logger.debug('init DownloadStandup')
#get AJarvis info
		self._pathAJarvis=config.get_path_AJarvis()
		self._userAJarvis=config.get_username_AJarvis()
		self._keyAJarvis=config.get_password_AJarvis()

#### PRIVATE METHODS ####

#### PUBLIC METHODS ####
	
	def get_link_download_audio(self, user, id_standup):
		self.logger.debug('request GET /download/%s with BasicHttpAuth', id_standup)

		response=requests.get(self._pathAJarvis+'/download/'+id_standup, auth=(self._userAJarvis, self._keyAJarvis), headers={ 'sub-user': user})

		if response and response.status_code != 200:
			return None, response.status_code

		return response.json()['download_url'], response.status_code