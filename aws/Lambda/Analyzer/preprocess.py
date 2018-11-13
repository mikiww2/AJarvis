
from loader import load_helper #, load_ignore_tokens
import logging, re

class Preprocess:
	def __init__(self):

		self.logger=logging.getLogger()
		self.logger.setLevel(logging.INFO)

		self.helper=load_helper();

		if self.helper:
			self.logger.info('Retrieve helper done')
			self.logger.info(self.helper)
		else:
			self.logger.warn('Error when retrieve helper, ignore helper assistance')

		#self.ignore_tokens=load_ignore_tokens();
		self.ignore_tokens=None

		if self.ignore_tokens:
			self.logger.info('Retrieve ignore_tokens done')
			self.logger.info(self.ignore_tokens)
		else:
			self.logger.warn('Error when retrieve ignore_tokens, cannot apply ignore_tokens insight')

	@staticmethod
	def _safe_replace(text, typo, correct):
		if text.lower().startswith(typo+' '):
			text=correct+text[len(typo):]

		if text.lower().endswith(' '+typo):
			text=text[:-len(typo)]+correct

		return re.sub(' '+typo+' ', ' '+correct+' ', text, flags=re.IGNORECASE)

	@staticmethod
	def get_punctuations():
		return ['.', '?', ',']

	@staticmethod
	def get_compact_tokens():
		return ['\'']

	@staticmethod
	def _remove_tokens(text, tokens):
		array=[]

		for token in text.lower().split(' '):
			if token not in tokens:
				array.append(token)

		return ' '.join(array)

	def _apply_helper(self, text):
		if self.helper:
			for typo, correct in self.helper['sentences'].items():
					text=self._safe_replace(text, typo, correct)

			for typo, correct in self.helper['tokens'].items():
					text=self._safe_replace(text, typo, correct)

		return text

	@staticmethod
	def remove_punctuation(text):
		return Preprocess._remove_tokens(text, Preprocess.get_punctuations())

	def remove_unnecessary_tokens(self, text):
		if not self.ignore_tokens:
			self.logger.error('Don\'t have ignore_tokens.json, ignore this op')
			return text

		return Preprocess._remove_tokens(text, self.ignore_tokens)

	def refine_text(self, text, helper=True):
		array=[]

		text=re.sub("[\(\[].*?[\)\]]", "", text)

		for elem in ["(", ")", "[", "]"]:
			text=text.replace(elem, '')

		for token in re.split('(\W+)', text):
			token=token.replace(' ', '')

			if token and token != '' and not token.isspace():
				array.append(token)

		text=' '.join(array)

		for char in Preprocess.get_compact_tokens():
			text=text.replace(' '+char+' ', char)

		if helper:
			text=self._apply_helper(text)

		return text
