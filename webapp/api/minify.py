from jsmin import jsmin
import logging, os, json


class Minify:
	@staticmethod
	def minify_js(Logger, config_file='config/minify_config.json'):
		file_dir=os.path.dirname(__file__)[:-4]+'/static/scripts/'

		logger=Logger.set_logger(logging.getLogger(__name__))

		logger.debug('Start logger')
		logger.debug('minify js files')


		with open(config_file, 'r') as file:
			config = json.load(file)

		if not config:
			logger.error('Cannot load %s', config_file)

		if not config['jobs']:
			logger.warn('no file to minify')

		for job in config['jobs']:
			if not job['type'] or not job['input'] or not job['output']:
				logger.error('Cannot load %s job', config_file)
#### concat files
			with open(file_dir+job['output']+'.'+job['type'], 'w') as out_file:
				for file in job['input']:
					with open(file_dir+file+'.'+job['type']) as in_file:
						out_file.write(in_file.read())
					out_file.write('\n')
#### uglify
			with open(file_dir+job['output']+'.'+job['type'], 'r') as in_file:
				with open(file_dir+job['output']+'.min.'+job['type'], 'w') as out_file:
					out_file.write(jsmin(in_file.read()))

			logger.info('done minify %s', file_dir+job['output']+'.min.'+job['type'])