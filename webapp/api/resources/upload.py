#!/usr/bin/env python3

import logging, requests, json #use of requests for connecting to AJarvis

class UploadStandup:
	def __init__(self, Logger, config):
#get logger
		self.logger=Logger.set_logger(logging.getLogger(__name__))
		self.logger.info('start logger')

		self.logger.debug('init UploadStandup')
#get AJarvis info
		self._pathAJarvis=config.get_path_AJarvis()
		self._userAJarvis=config.get_username_AJarvis()
		self._keyAJarvis=config.get_password_AJarvis()

#### PRIVATE METHODS ####

#### PUBLIC METHODS ####
	
	def get_link_upload_audio(self, user):
		self.logger.debug('request GET /upload/link with BasicHttpAuth')

		response=requests.get(self._pathAJarvis+'/upload/link', auth=(self._userAJarvis, self._keyAJarvis), headers={ 'sub-user': user})

		if response and response.status_code != 200:
			return None, response.status_code

		return response.json()['upload_url'], response.status_code
		
	def upload_text(self, text, user):
		#prepare text
		text=text.replace('\n', ' ')
		text=text.replace('\r', '')
		
		self.logger.debug('request POST /upload somewhere path with BasicHttpAuth')
		
		response=None
		payload={ "standup": text }

		response=requests.post(self._pathAJarvis+'/upload/text', auth=(self._userAJarvis, self._keyAJarvis), headers={ 'sub-user': user}, json=payload)

		if response and response.status_code != 200:
			self.logger.error(response)
			return True

		return False

'''
	def upload(self, user, flask_request_file_stream): #change name maybe
#save file locally for testing
		file_name='audio.wav'

		audio_type=flask_request_file_stream.mimetype
		audio_name='standupaudio' # here change filename

		with open(file_name, "wb") as file: #wb is write binary
			file.write(flask_request_file_stream.read())
			self.logger.debug('%s: %s save as %s',audio_name, audio_type, file_name)

		flask_request_file_stream.seek(0) #saving audio.wav use the stream
#processing file
		#converto, modifico o altro

		#https://stackoverflow.com/questions/23925494/how-to-convert-wav-to-flac-from-python
		#http://audiotools.sourceforge.net/install.html


		#https://docs.python.org/3/library/wave.html
		#import wave    # need to get audio constrains from getMediaDevice, not needed for now


		#csum=checksumMD5(audio.stream)
		#import hashlib
		#hasher = hashlib.md5()
		#with open('myfile.jpg', 'rb') as afile:
	    #	buf = afile.read()
	    #	hasher.update(buf)
		#print(hasher.hexdigest())

		#audio.seek(0) #checksumMD5 use the stream

		#response=requests.post(myurl, auth=myauth, files=payload, headers={"X-Auth-Token": token, "Checksum": c, "File-Size": actualSize})


		#req=requests.Request('GET', self._pathAJarvis+'/upload/link')
		#req=req.prepare()
		s#elf.logger.debug(Utils.print_requests(req))
		#s=requests.Session()
		#response=s.send(req)

#get upload presigned url
		self.logger.debug('request GET /upload/link with BasicHttpAuth')

		response=requests.get(self._pathAJarvis+'/upload/link', auth=(self._userAJarvis, self._keyAJarvis), headers={ 'sub-user': user })

		if response and response.status_code == 401:
			return response.status_code

		upload_url=response.json()['upload_url']

		self.logger.info('GET /upload/link status %s, link upload = %s', response.status_code, upload_url)
#upload audio
		headers={ 'Content-type': audio_type}

		files={'file': (audio_name, flask_request_file_stream.stream, audio_type)}

		self.logger.debug('headers = %s, files = %s', headers, files)

		response=requests.put(upload_url, headers=headers, files=files)

		#####

		self.logger.info('PUT audio.wav status %s', response.status_code)
		self.logger.debug('response from AJarvis: %s', response)

		if response and response.status_code == 200:
			return None
		return response.status_code
'''
