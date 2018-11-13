
import flask, logging, json

from api.minify import Minify
from api.resources.autentication import Autentication
from api.resources.configuration import Configuration
from api.resources.detail import DetailAudio
from api.resources.upload import UploadStandup
from api.resources.download import DownloadStandup

class App:
	def __init__(self, Logger):
		self.Logger=Logger
		self.app=flask.Flask(__name__, static_folder='../static', template_folder='../templates/')
		#flask.session.permanent = True #needed ? default session active until browser is closed
##### setup logger ####
		self.logger=Logger.set_logger(logging.getLogger(__name__))
		self.logger.debug('Start logger')
#### setup api class####
		self.config=Configuration(Logger)
		autentication=Autentication(Logger)
		uploadStandup=UploadStandup(Logger, self.config)
		downloadStandup=DownloadStandup(Logger, self.config)
		detailAudio=DetailAudio(Logger, self.config)
#### session key ####
		#if app refresh than all session is lost
		self.app.secret_key=self.config.get_session_key()

		#remove ugly whitespace with render_template
		#self.app.jinja_env.trim_blocks=True
		self.app.jinja_env.lstrip_blocks=True

#### PRIVATE METHODS ####

		def _is_logged():
			if 'username' in flask.session:
				return True #logged
			return False #not logged

#### ROUTES ####

		@self.app.route("/")
		def index():
			if not _is_logged():
				self.logger.debug('call index when not logged, redirect to login')
				return flask.redirect(flask.url_for('login'))

			self.logger.debug('user %s call /', flask.session['username'])
			return flask.render_template('index.html', username=flask.session['username'])
####
		@self.app.route("/recorder")
		def recorder():
			if not _is_logged():
				self.logger.debug('call index when not logged, redirect to login')
				return flask.redirect(flask.url_for('login'))

			self.logger.debug('user %s call /recorder', flask.session['username'])
			return flask.render_template('recorder.html', username=flask.session['username'])
####
		@self.app.route("/upload/standup", methods=['GET', 'POST'])
		def upload_text():
			if not _is_logged():
				self.logger.debug('call upload_text when not logged, redirect to login')
				return flask.redirect(flask.url_for('login'))
			
			if flask.request.method != 'POST':
				self.logger.debug('call upload_text without POST, show form')
				return flask.render_template('text.html', username=flask.session['username'])
			
			self.logger.debug('user %s call POST /upload_text', flask.session['username'])

			standup=flask.request.form['standup']
			
			error=uploadStandup.upload_text(standup, flask.session['username'])
			
			if error:
				message=['Caricamento trascrizione standup non riuscito', 'danger']
				
				return flask.render_template('text.html', username=flask.session['username'], standup=standup, message=message)
			
			message=['Caricamento trascrizione standup riuscito', 'success']
			
			return flask.render_template('text.html', username=flask.session['username'], message=message)	
####
		@self.app.route("/list")
		def list():
			if not _is_logged():
				self.logger.debug('call list when not logged, redirect to login')
				return flask.redirect(flask.url_for('login'))

			self.logger.debug('user %s call /list', flask.session['username'])

			items, error =detailAudio.get_list(flask.session['username'])

			if error:
				self.logger.error('something goes wrong')
				return flask.render_template('list.html', username=flask.session['username'], message=['Non sono riuscito a caricare la lista delle standup', 'danger'])
				
			return flask.render_template('list.html', username=flask.session['username'], items=items)
####
		@self.app.route("/projects")
		def projects():
			if not _is_logged():
				self.logger.debug('call projects when not logged, redirect to login')
				return flask.redirect(flask.url_for('login'))

			self.logger.debug('user %s call /projects', flask.session['username'])

			items, error =detailAudio.get_projects(flask.session['username'])

			if error:
				self.logger.error('something goes wrong')
				return flask.render_template('projects.html', username=flask.session['username'], message=['Non sono riuscito a caricare la lista dei progetti', 'danger'])
				
			return flask.render_template('projects.html', username=flask.session['username'], projects=items)
####
		@self.app.route("/login", methods=['GET', 'POST'])
		def login():
			if _is_logged():
				self.logger.debug('call login when logged as %s', flask.session['username'])
				return flask.redirect(flask.url_for('index'))

			if flask.request.method != 'POST':
				self.logger.debug('call login without POST, show form')
				return flask.render_template('login.html')

			self.logger.debug('call login with POST, perform login')
			self.logger.debug('request : %s', json.dumps(flask.request.form.to_dict(flat=False))) #immutablemultidict to json

			username=flask.request.form['username']
			password=flask.request.form['password']

			if not username or username == '' or not password or password == '':
				self.logger.error('login_info not valid')
				return flask.render_template('login.html')
			
			#authenticate
			if autentication.autenticate(username, password):
				flask.session['username']=username
				self.logger.info('%s logged, redirect to index', username)

				return flask.redirect(flask.url_for('index'))
			
			self.logger.info('username or password wrong, redirect to login')
			return flask.render_template('login.html', message=['Username o password errati, riprova', 'danger'])
####
		@self.app.route("/logout")
		def logout():
			if not _is_logged():
				self.logger.debug('call loguot when not logged')
				return flask.redirect(flask.url_for('login'))
			
			self.logger.debug('%s call logout', flask.session['username'])
			flask.session.pop('username', None)

			self.logger.info('logout successfully, redirect to login')
			return flask.redirect(flask.url_for('login'))

####
		@self.app.route("/upload/link", methods=['GET'])
		def get_upload_link():
			if not _is_logged():
				self.logger.debug('GET /upload/link when not logged, redirect to login')
				return ''

			upload_url, status =uploadStandup.get_link_upload_audio(flask.session['username'])

			if status != 200 or not upload_url:
				self.logger.error('cannot GET /upload/link')
				return ''

			return upload_url

####
		@self.app.route("/download/link/<id_standup>", methods=['GET'])
		def get_download_link(id_standup):
			if not _is_logged():
				self.logger.debug('GET /download/link when not logged, redirect to login')
				return ''

			download_url, status =downloadStandup.get_link_download_audio(flask.session['username'], id_standup)

			if status != 200 or not download_url:
				self.logger.error('cannot GET /download/link')
				return ''

			return download_url
			
####
		@self.app.route("/detail/<id_standup>", methods=['GET'])
		def show_detail(id_standup):
			if not _is_logged():
				self.logger.debug('detail info when not logged, why this is happening. btw .... redirect to login') #come fa uno non loggato caricare?
				return flask.redirect(flask.url_for('login'))

			self.logger.debug('user %s call /detail/%s', flask.session['username'], id_standup)

			result, error =detailAudio.get_detail(flask.session['username'], id_standup, True)

			if error:
				self.logger.error('audio %s not found', id_standup)
				message='audio '+id_standup+' not found'
				flask.render_template('error.html', error='audio '), error

			return flask.render_template('detail.html', username=flask.session['username'], item=result)

#### ERRORS ####

		@self.app.errorhandler(404)
		def page_not_found(e):
			return flask.render_template('error.html', error=e), 404

		@self.app.errorhandler(405)
		def page_not_found(e):
			return flask.render_template('error.html', error=e), 405

####

	def create_app(self):

		Minify.minify_js(self.Logger)

		return self.app, self.config.get_app_config()
