#!/usr/bin/env python3

import logging, requests, json
from datetime import datetime

class DetailAudio:
	#init
	def __init__(self, Logger, config):
#get logger
		self.logger=Logger.set_logger(logging.getLogger(__name__))
		self.logger.info('start logger')

		self.logger.debug('init DetailAudio')
#get AJarvis info
		self._pathAJarvis=config.get_path_AJarvis()
		self._userAJarvis=config.get_username_AJarvis()
		self._keyAJarvis=config.get_password_AJarvis()

	@staticmethod
	def _tags_to_string(tags):
		if not tags:
			return ''
		return '< '+(', '.join(tags))+' >'

#retrieve id_audio info
	def get_detail(self, user, id_audio, show_all=False):

		payload={
			'id': str(id_audio),
			'show': ['status', 'text']
		}

		if show_all:
			payload['show']+= ['project', 'person', 'yesterday', 'today', 'issue', 'duration']

		response=self._retrieve_standup_request(user, payload, 'ONE')

		if response and response.status_code != 200:
			return None, response.status_code

		self.logger.debug(response.json())

		standup=response.json()['items'][0]

		if 'yesterday' in standup:
			for sentence in standup['yesterday']:
				sentence['tags']=DetailAudio._tags_to_string(sentence['tags'])

		if 'today' in standup:
			for sentence in standup['today']:
				sentence['tags']=DetailAudio._tags_to_string(sentence['tags'])

		if 'issue' in standup:
			for sentence in standup['issue']:
				sentence['tags']=DetailAudio._tags_to_string(sentence['tags'])

		if 'duration' in standup:
			for sentence in standup['duration']:
				sentence['tags']=DetailAudio._tags_to_string(sentence['tags'])

				if 'valutation' in sentence:
					sentence['valutation']=DetailAudio._tags_to_string(sentence['valutation'])

		standup['date']=datetime.strptime(standup['id'], '%Y-%m-%dT%H-%M-%S').strftime('%d/%m/%Y')

		self.logger.info('standup after make-up: %s', standup)

		return standup, None

#retrieve all audio info
	def get_list(self,user):

		payload={
				'show': ['status', 'text']
			}

		response=self._retrieve_standup_request(user, payload, 'ALL')

		if response and response.status_code != 200:
			return None, response.status_code

		self.logger.debug(response.json())

		return response.json()['items'], None

	def _retrieve_standup_request(self, user, payload, range_request=None):
		if range_request and range_request in ['ALL', 'DAY', 'ONE']:
			path=self._pathAJarvis+'/standup/retrieve/'+range_request
		else:
			self.logger.error('range = %s not valid, select without range', range_request)
			path=self._pathAJarvis+'/standup/retrieve'

		self.logger.debug('POST %s', path)
		return requests.post(path, auth=(self._userAJarvis, self._keyAJarvis), headers={'sub-user': user}, data=json.dumps(payload))

#retrieve projects  info
	def get_projects(self, user):

		path=self._pathAJarvis+'/project/all'

		response=requests.get(path, auth=(self._userAJarvis, self._keyAJarvis), headers={'sub-user': user})

		if response and response.status_code != 200:
			return None, response.status_code

		self.logger.debug(response.json())

		projects=response.json()['projects']

		for project in projects:
			for standup in project['standups']:
				if 'yesterday' in standup:
					s=''
					for sentence in standup['yesterday']:
						s+=DetailAudio._tags_to_string(sentence['tags'])+' '

					standup['yesterday']=s

				if 'today' in standup:
					s=''

					for sentence in standup['today']:
						s+=DetailAudio._tags_to_string(sentence['tags'])+' '

					standup['today']=s

				if 'issue' in standup:
					for sentence in standup['issue']:
						sentence['tags']=DetailAudio._tags_to_string(sentence['tags'])
						if sentence['valutation'] == 'POSITIVE':
							sentence['valutation']='success'
						elif sentence['valutation'] == 'NEGATIVE':
							sentence['valutation']='danger'
						else:
							sentence['valutation']='warning'

				if 'duration' in standup:
					for sentence in standup['duration']:
						sentence['tags']=DetailAudio._tags_to_string(sentence['tags'])
						if 'valutation' in sentence:
							sentence['valutation']=DetailAudio._tags_to_string(sentence['valutation'])

				standup['date']=datetime.strptime(standup['id'], '%Y-%m-%dT%H-%M-%S').strftime('%d/%m/%Y')

		self.logger.info('projects after make-up: %s', projects)

		return projects, None

