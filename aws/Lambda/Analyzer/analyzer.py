
import copy, logging, re, json

from preprocess import Preprocess
from loader import load_tokens
from comprehend import dominant_language, key_phrases, sentiment

class Analyzer:
	def __init__(self):
		self.logger=logging.getLogger()
		self.logger.setLevel(logging.INFO)

		self.INFORMATION={}
		self.preprocess=Preprocess()

		tokens=load_tokens()
		self.logger.info('tokens.json: %s', tokens)

		##prepare tokens
		self.IDENTIFIERS=[]
		self.DICTIONARY_TOKENS={}
		self.DICTIONARY_TOKENS['PROJECT_IDENTIFIERS']={}
		self.DICTIONARY_TOKENS['PERSON_IDENTIFIERS']={}
		self.DICTIONARY_TOKENS['YESTERDAY_SECTION_IDENTIFIERS']={}
		self.DICTIONARY_TOKENS['TODAY_SECTION_IDENTIFIERS']={}
		self.DICTIONARY_TOKENS['ISSUE_SECTION_IDENTIFIERS']={}
		self.DICTIONARY_TOKENS['DURATION_IDENTIFIERS']={}

		for token in tokens['tokens']:
			for key, value in token.items():
				self.IDENTIFIERS.append(key)

				if value['type'] not in self.DICTIONARY_TOKENS.keys():
					self.logger.info('Value *%s* not in DICTIONARY_TOKENS, will ignore token', value['type'])
				else:
					self.DICTIONARY_TOKENS[value['type']][key]=copy.deepcopy(value)

		self.logger.info('IDENTIFIERS: %s', self.IDENTIFIERS)
		self.logger.info('DICTIONARY_TOKENS: %s', self.DICTIONARY_TOKENS)

		self.END_LINES=[]

		if 'end_lines' in tokens:
			for elem in tokens['end_lines']:
				self.END_LINES.append(elem)
		else:
			self.logger.error('Error when retrieve end_lines, tokens.json may be corrupt')

		self.IGNORE_TOKENS=[]

		if 'ignore_tokens' in tokens:
			for elem in tokens['ignore_tokens']:
				self.IGNORE_TOKENS.append(elem)
		else:
			self.logger.error('Error when retrieve ignore_tokens, tokens.json may be corrupt')

		self.ISSUE_VALUTATION={}

		if 'issue_valutation' in tokens:
			for key in tokens['issue_valutation'].keys():
				self.ISSUE_VALUTATION[key]=tokens['issue_valutation'][key]
		else:
			self.logger.error('Error when retrieve issue_valutation, tokens.json may be corrupt')

		self.DURATION_VALUTATION={}

		if 'duration_valutation' in tokens:
			for key in tokens['duration_valutation'].keys():
				self.DURATION_VALUTATION[key]=tokens['duration_valutation'][key]
		else:
			self.logger.error('Error when retrieve duration_valutation, tokens.json may be corrupt')


		self.IGNORE_TAGS=[]

		if 'ignore_tags' in tokens:
			for token in tokens['ignore_tags']:
				self.IGNORE_TAGS.append(token)
		else:
			self.logger.warn('Error when retrieve ignore_tags, tokens.json may be corrupt')


	@staticmethod
	def _remove_token(sentence, token):
		sentence=sentence.replace(' '+token+' ', ' ')
		if sentence.startswith(token+' '):
			sentence=sentence[len(token)+1:]
		if sentence.endswith(' '+token):
			sentence=sentence[:-(len(token)+1)]

		return sentence


	def _detect_project_name(self):
		
		def _naive_find_project_name():
			self.logger.info('Naive algorithm for project name, expect in 1-2 key phrases')

			identifiers=[]
			for elem in self.DICTIONARY_TOKENS['PROJECT_IDENTIFIERS'].keys():
				for sentence in self.DICTIONARY_TOKENS['PROJECT_IDENTIFIERS'][elem]['sentences']:
					sentence=sentence.replace('# ', '')
					sentence=sentence.replace(' #', '')
					
					identifiers.append(sentence)
			self.logger.info('identifiers: %s', identifiers)

			for identifier in identifiers:

				if identifier == self.KEY_PHRASES[0].lower() and self.KEY_PHRASES[1].lower() not in self.IDENTIFIERS:
					self.logger.info('Found identifier *%s*, expect project name is *%s*', identifier, self.KEY_PHRASES[1])

					self.KEY_PHRASES_IDENTIFIER+=2
					return self.KEY_PHRASES[1].lower()

				elif self.KEY_PHRASES[0].lower().startswith(identifier):

					self.logger.info('Found identifier *%s*, expect project name is *%s*', identifier, self.KEY_PHRASES[0][len(identifier)+1:])

					self.KEY_PHRASES_IDENTIFIER+=1
					return self.KEY_PHRASES[0][len(identifier)+1:].lower()
			
			return None

		def _manual_find_project_name():
			pass

		project_name=_naive_find_project_name()

		if project_name:
			self.INFORMATION['PROJECT_NAME']=project_name
			return project_name
		
		self.logger.warn('Cannot found project name with naive algorithm')
		self.logger.error('Don\'t have a solution for now')

		return None

	def _detect_person_name(self):

		def _naive_find_person_name():
			self.logger.info('Naive algorithm for person name, expect in 1 key phrases')

			identifiers=copy.deepcopy(list(self.DICTIONARY_TOKENS['PERSON_IDENTIFIERS'].keys()))
			identifiers=copy.deepcopy(list(self.DICTIONARY_TOKENS['YESTERDAY_SECTION_IDENTIFIERS'].keys()))
			identifiers=copy.deepcopy(list(self.DICTIONARY_TOKENS['TODAY_SECTION_IDENTIFIERS'].keys()))

			if self.KEY_PHRASES[self.KEY_PHRASES_IDENTIFIER] not in identifiers and self.KEY_PHRASES[self.KEY_PHRASES_IDENTIFIER+1] in identifiers:
				if self.KEY_PHRASES[self.KEY_PHRASES_IDENTIFIER] in self.INFORMATION['PROJECT_NAME']:
					return None

				person_name=self.KEY_PHRASES[self.KEY_PHRASES_IDENTIFIER]
				self.logger.info('Found identifier *%s*, expect person name *%s*', self.KEY_PHRASES[self.KEY_PHRASES_IDENTIFIER+1], person_name)

				self.KEY_PHRASES_IDENTIFIER+=1

				if self.KEY_PHRASES[self.KEY_PHRASES_IDENTIFIER] in self.DICTIONARY_TOKENS['PERSON_IDENTIFIERS'].keys():
					self.KEY_PHRASES_IDENTIFIER+=1

				self.INFORMATION['PERSON_NAME']=person_name
				return person_name

			self.INFORMATION['PERSON_NAME']='None'
			return None

		def _manual_find_person_name():
			temp_text=self.TEXT
			person_name=None

			if 'PROJECT_NAME' in self.INFORMATION:
				temp_text=temp_text.split(self.INFORMATION['PROJECT_NAME'])[1]

			identifiers=copy.deepcopy(list(self.DICTIONARY_TOKENS['YESTERDAY_SECTION_IDENTIFIERS'].keys()))
			identifiers+=copy.deepcopy(list(self.DICTIONARY_TOKENS['TODAY_SECTION_IDENTIFIERS'].keys()))

			for identifier in identifiers:
				temp_text=temp_text.split(identifier)[0]

			temp_text=self.preprocess.remove_punctuation(temp_text)
			#temp_text=self.preprocess.remove_unnecessary_tokens(temp_text)
			for elem in self._get_end_lines():
				temp_text=Analyzer._remove_token(temp_text, elem)

			if temp_text.startswith(' '):
				temp_text=temp_text[1:]
			if temp_text.endswith(' '):
				temp_text=temp_text[:-1]

			self.logger.info('Reduce checking text to *%s*', temp_text)
			
			for identifier in self.DICTIONARY_TOKENS['PERSON_IDENTIFIERS'].keys():
				if identifier in temp_text:
					self.logger.warn('Found identifier *%s*, check *%s*', identifier, temp_text)

					for sentence in self.DICTIONARY_TOKENS['PERSON_IDENTIFIERS'][identifier]['sentences']:
						pattern=identifier.replace(identifier+' ','')
						pattern=pattern.replace(' '+identifier,'')

						if pattern in temp_text:

							if sentence.startswith('#'):
								person_name=temp_text.split(' '+pattern)[0]

							elif sentence.endswith('#'):
								person_name=temp_text.split(pattern+' ')[1]

							else:
								self.logger.error('Cannot use pattern *%s*', sentence)
								break


							if person_name and person_name != '' and person_name != sentence:
								self.INFORMATION['PERSON_NAME']=person_name
								self.logger.warn('Expect person name *%s*', person_name)

								return person_name

			self.INFORMATION['PERSON_NAME']='None'
			return None

		person_name=_naive_find_person_name()

		if not person_name:
			self.logger.warn('Cannot found person name with naive algorithm, rollback to manual search')

			person_name=_manual_find_person_name()

			if not person_name:
				self.logger.error('Don\'t have a solution for now')
				return None

		return person_name.lower()


	def find_sections(self):

		def _detect_identifier(sentence, last):
			now=None

			if sentence and sentence != '' and not sentence.isspace():
				for token in self.DICTIONARY_TOKENS['YESTERDAY_SECTION_IDENTIFIERS'].keys():
					if token in sentence:
						self.SECTION['YESTERDAY'].append(sentence)
						now='YESTERDAY'
						break

				for token in self.DICTIONARY_TOKENS['TODAY_SECTION_IDENTIFIERS'].keys():
					if token in sentence:
						self.SECTION['TODAY'].append(sentence)
						now='TODAY'
						break

				for token in self.DICTIONARY_TOKENS['ISSUE_SECTION_IDENTIFIERS'].keys():
					if token in sentence:
						self.SECTION['ISSUE'].append(sentence)
						now='ISSUE'
						break

				for token in self.DICTIONARY_TOKENS['DURATION_IDENTIFIERS'].keys():
					if token in sentence:
						self.SECTION['DURATION'].append(sentence)
						now='DURATION'
						break

				if not now:
					if last:
						self.logger.error('Cannot identify type section of *%s*, add to %s', sentence, last)

						self.SECTION[last][-1]=self.SECTION[last][-1]+' , '+sentence
					else:
						self.logger.error('Cannot identify type section of *%s*, ignore it', sentence)
			return now

		
		temp_text=self.TEXT

		if 'PERSON_NAME' in self.INFORMATION:
			identifier=self.INFORMATION['PERSON_NAME']
		elif 'PROJECT_NAME' in self.INFORMATION:
			identifier=self.INFORMATION['PROJECT_NAME']
		else:
			identifier=None

		if identifier:
			temp_text=identifier.join(temp_text.split(identifier)[1:])


		self.SECTION={}
		self.SECTION['YESTERDAY']=[]
		self.SECTION['TODAY']=[]
		self.SECTION['ISSUE']=[]
		self.SECTION['DURATION']=[]

		end_line=['.', '!', '?']

		phrases=['']

		for token in temp_text.split(' '):
			phrases[-1]=phrases[-1]+' '+token

			if token in end_line:
				phrases[-1]=phrases[-1][1:]
				phrases.append('')

		if phrases[-1] == '':
			del phrases[-1]

		self.logger.info(phrases)

		last=None

		for phrase in phrases:
			#phrase=self.preprocess.remove_punctuation(phrase)
			#phrase=self.preprocess.remove_unnecessary_tokens(phrase)

			phrase=self.preprocess.refine_text(phrase, False)

			self.logger.info('Compacted in *%s*', phrase)

			last=_detect_identifier(phrase,last)

		######

		self.INFORMATION['YESTERDAY']=[]
		self.INFORMATION['TODAY']=[]
		self.INFORMATION['ISSUE']=[]
		self.INFORMATION['DURATION']=[]

		for sentence in self.SECTION['YESTERDAY']:
			self.find_yesterday_information(sentence)

		for sentence in self.SECTION['TODAY']:
			self.find_today_information(sentence)

		for sentence in self.SECTION['ISSUE']:
			self.find_issue_information(sentence)

		for sentence in self.SECTION['DURATION']:
			self.find_duration_information(sentence)
	
	def _get_end_lines(self):
		return self.END_LINES

	def _reduce_section(self, sentence, found_section_tokens, found_other_section_tokens):

			for end_line in self._get_end_lines():
				array=sentence.split(end_line)
				
				if len(array) > 1:
					part=array[0]
					
					for elem in array[1:]:
						if not part or part == '' or part.isspace():
							part=elem
							break
						elif not elem or elem == '' or elem.isspace():
							break
						else:
							found_other_first=False
							found_other_second=False
							found_first=False
							found_second=False
							
							for identifier in found_section_tokens:
								if identifier in part:
									found_first=True
									
								if identifier in elem:
									found_second=True
							
							for identifier in found_other_section_tokens:
								if identifier in part:
									found_other_first=True
									
								if identifier in elem:
									found_other_second=True
							
							if found_other_first and not found_first:
								self.logger.info('*%s* will be ignored', part)
								part=elem
							
							elif found_other_second and not found_second:
								self.logger.info('*%s* will be ignored', elem)
								
							else:
								part=part+end_line+elem
					sentence=part

			for elem in self._get_end_lines():
				sentence=Analyzer._remove_token(sentence, elem)

			sentence=self.preprocess.refine_text(sentence, False)

			return sentence

	def extract_tags(self, sentence, dictionary_keys):

		def _squeeze_informations(sentence):
			tokens=[]

			for key_phrase in self.KEY_PHRASES:
				key_phrase=key_phrase.lower()

				for elem in self._get_end_lines():
					key_phrase=Analyzer._remove_token(key_phrase, elem)

				key_phrase=self.preprocess.refine_text(key_phrase, False)





				if sentence == key_phrase or sentence.startswith(key_phrase+' ') or sentence.endswith(' '+key_phrase)or ' '+key_phrase+' ' in sentence:
					tokens.append(key_phrase)

			return tokens

		def _find_important_tokens(tokens, identifiers):
			array=[]
			for token in tokens:
				found=False
				for identifier in identifiers:
					if identifier in token.lower():
						found=True
						break
				if not found:
					array.append(token)

			return array

		def _tagger(key_phrases):
			if not self.IGNORE_TAGS:
				return key_phrases

			array=[]

			for temp_key in key_phrases:

				for tag in self.IGNORE_TAGS:
					if not temp_key and temp_key == '' and temp_key.isspace():
						break

					if temp_key == tag:
						temp_key=''
						break

					temp_key=Analyzer._remove_token(temp_key, tag)

				temp_key=Analyzer._remove_token(temp_key, '') #remove ' ' from start and end

				if temp_key and temp_key != '' and not temp_key.isspace():
					array.append(temp_key)

			tags=[]
			for elem in array:
				if elem not in tags:
					tags.append(elem)

			return tags

		tokens=_squeeze_informations(sentence)
		self.logger.info('Tokens: %s', tokens)

		important_tokens=_find_important_tokens(tokens, dictionary_keys)
		self.logger.info('Important tokens: %s', important_tokens)

		return _tagger(important_tokens)

	
	def find_yesterday_information(self, sentence):
		self.logger.info('YESTERDAY : *%s*', sentence)
		
		found_section_tokens=[]
		found_other_section_tokens=[]
		
		for identifier in self.DICTIONARY_TOKENS['YESTERDAY_SECTION_IDENTIFIERS'].keys():
			if identifier in sentence:
				found_section_tokens.append(identifier)
		
		identifiers=copy.deepcopy(list(self.DICTIONARY_TOKENS['TODAY_SECTION_IDENTIFIERS'].keys()))
		identifiers+=copy.deepcopy(list(self.DICTIONARY_TOKENS['ISSUE_SECTION_IDENTIFIERS'].keys()))
		identifiers+=copy.deepcopy(list(self.DICTIONARY_TOKENS['DURATION_IDENTIFIERS'].keys()))
		
		for identifier in identifiers:
			if identifier in sentence:
				found_other_section_tokens.append(identifier)


		if len(found_other_section_tokens) > 0:
			sentence=self._reduce_section(sentence, found_section_tokens, found_other_section_tokens)

		self.logger.info('YESTERDAY remaining phrase is *%s*',sentence)

		info={}
		info['sentence']=sentence

		info['tags']=self.extract_tags(sentence, self.DICTIONARY_TOKENS['YESTERDAY_SECTION_IDENTIFIERS'].keys())

		if not info['tags']:
			self.logger.error('Cannot find any information from *%s*, will ignore it', sentence)
			
		else:
			self.INFORMATION['YESTERDAY'].append(info)
			self.logger.info(info)


	def find_today_information(self, sentence):
		self.logger.info('TODAY : *%s*', sentence)
		
		found_section_tokens=[]
		found_other_section_tokens=[]
		
		for identifier in self.DICTIONARY_TOKENS['TODAY_SECTION_IDENTIFIERS'].keys():
			if identifier in sentence:
				found_section_tokens.append(identifier)
		
		identifiers=copy.deepcopy(list(self.DICTIONARY_TOKENS['YESTERDAY_SECTION_IDENTIFIERS'].keys()))
		identifiers+=copy.deepcopy(list(self.DICTIONARY_TOKENS['ISSUE_SECTION_IDENTIFIERS'].keys()))
		identifiers+=copy.deepcopy(list(self.DICTIONARY_TOKENS['DURATION_IDENTIFIERS'].keys()))
		
		for identifier in identifiers:
			if identifier in sentence:
				found_other_section_tokens.append(identifier)


		if len(found_other_section_tokens) > 0:
			sentence=self._reduce_section(sentence, found_section_tokens, found_other_section_tokens)

		self.logger.info('TODAY remaining phrase is *%s*',sentence)

		info={}
		info['sentence']=sentence

		info['tags']=self.extract_tags(sentence, self.DICTIONARY_TOKENS['TODAY_SECTION_IDENTIFIERS'].keys())

		if not info['tags']:
			self.logger.error('Cannot find any information from *%s*, will ignore it', sentence)
			
		else:
			self.INFORMATION['TODAY'].append(info)
			self.logger.info(info)
		

	def find_issue_information(self, sentence):

		def valutation(len_tags, sentence):

			def _weight(sentiment_type):
				if sentiment_type=='NEGATIVE':
					return -1
				elif sentiment_type=='POSITIVE':
					return 1
				elif sentiment_type== 'NEUTRAL' or sentiment_type=='MIXED':
					return 0
				
				self.logger.warn('Cannot weight sentiment_type %s', sentiment_type)
				return 0

			def with_tag(sentence):
				array=[]
				for token in sentence.split(' '):
					for elem in self.ISSUE_VALUTATION.keys():
						if elem == token:
							array.append(self.ISSUE_VALUTATION[elem])

				if not len(array) or 'MIXED' in array:
					return 0

				count=0
				for elem in array:
					count+=_weight(elem)

				return count

			valutation=with_tag(sentence)

			if valutation == 0:
				self.logger.warn('Cannot identify weight only with tag, try with other things')

				if not len_tags:
					return None

				valutate_sentiment=sentiment(sentence)
				self.logger.info('sentiment: %s', valutate_sentiment)

				weight=_weight(valutate_sentiment['Sentiment'])
				if not weight:
					return "NEUTRAL"

				elif weight > 0:
					return "POSITIVE"
				
				return "NEGATIVE"

			elif valutation > 0:
				return "POSITIVE"

			return "NEGATIVE"

		
		self.logger.info('ISSUE : *%s*', sentence)
		
		found_section_tokens=[]
		found_other_section_tokens=[]
		
		for identifier in self.DICTIONARY_TOKENS['ISSUE_SECTION_IDENTIFIERS'].keys():
			if identifier in sentence:
				found_section_tokens.append(identifier)
		
		identifiers=copy.deepcopy(list(self.DICTIONARY_TOKENS['YESTERDAY_SECTION_IDENTIFIERS'].keys()))
		identifiers+=copy.deepcopy(list(self.DICTIONARY_TOKENS['TODAY_SECTION_IDENTIFIERS'].keys()))
		identifiers+=copy.deepcopy(list(self.DICTIONARY_TOKENS['DURATION_IDENTIFIERS'].keys()))
		
		for identifier in identifiers:
			if identifier in sentence:
				found_other_section_tokens.append(identifier)


		if found_other_section_tokens:
			sentence=self._reduce_section(sentence, found_section_tokens, found_other_section_tokens)

		self.logger.info('ISSUE remaining phrase is *%s*',sentence)
		info={}
		info['sentence']=sentence

		info['tags']=self.extract_tags(sentence, self.DICTIONARY_TOKENS['ISSUE_SECTION_IDENTIFIERS'].keys())

		issue_valutation=valutation(len(info['tags']), sentence)


		if not issue_valutation:
			self.logger.error('Cannot find any information from *%s*, will ignore it', sentence)
			
		else:
			info['valutation']=issue_valutation

			self.INFORMATION['ISSUE'].append(info)
			self.logger.info(info)


	def find_duration_information(self, sentence):

		def valutation(tags):

			s= ' '.join(tags)

			array={}
			for tag in self.DURATION_VALUTATION.keys():
				if tag in s:
					array[tag]=self.DURATION_VALUTATION[tag]

			if array:
				return array
			else:
				return None


		self.logger.info('DURATION : *%s*', sentence)
		
		found_section_tokens=[]
		found_other_section_tokens=[]
		
		for identifier in self.DICTIONARY_TOKENS['DURATION_IDENTIFIERS'].keys():
			if identifier in sentence:
				found_section_tokens.append(identifier)
		
		identifiers=copy.deepcopy(list(self.DICTIONARY_TOKENS['YESTERDAY_SECTION_IDENTIFIERS'].keys()))
		identifiers+=copy.deepcopy(list(self.DICTIONARY_TOKENS['TODAY_SECTION_IDENTIFIERS'].keys()))
		identifiers+=copy.deepcopy(list(self.DICTIONARY_TOKENS['ISSUE_SECTION_IDENTIFIERS'].keys()))
		
		for identifier in identifiers:
			if identifier in sentence:
				found_other_section_tokens.append(identifier)

		if len(found_other_section_tokens) > 0:
			sentence=self._reduce_section(sentence, found_section_tokens, found_other_section_tokens)

		self.logger.info('DURATION remaining phrase is *%s*',sentence)

		info={}
		info['sentence']=sentence

		info['tags']=self.extract_tags(sentence, self.DICTIONARY_TOKENS['DURATION_IDENTIFIERS'].keys())

		duration_valutation=valutation(info['tags'])

		if duration_valutation:
			array=[]
			for tag in info['tags']:
				if tag not in duration_valutation.keys():
					array.append(tag)

			valutations=[]
			for elem in duration_valutation.keys():
				valutations.append(duration_valutation[elem])

			info['tags']=array
			info['valutation']=valutations

		if not info['tags']:
			self.logger.error('Cannot find any information from *%s*, will ignore it', sentence)
			
		else:
			self.INFORMATION['DURATION'].append(info)
			self.logger.info(info)
			

	def analyze(self, text):
		self.INFORMATION={}
		self.ORIGINAL_TEXT=text
		self.logger.info('ORIGINAL_TEXT: %s', self.ORIGINAL_TEXT)

		self.TEXT=self.ORIGINAL_TEXT
		self.TEXT=self.preprocess.refine_text(self.TEXT)
		self.INFORMATION['TEXT']=self.TEXT
		self.logger.info('TEXT: %s', self.TEXT)

		self.LANGUAGE=dominant_language(self.TEXT)
		if self.LANGUAGE != 'en':
			self.logger.error('%s is the dominant language, except wrong analysis', self.LANGUAGE)

		self.KEY_PHRASES=key_phrases(self.TEXT)
		self.KEY_PHRASES_IDENTIFIER=0
		self.logger.info('KEY_PHRASES: %s', self.KEY_PHRASES)




		self.TEXT=self.TEXT.lower()

		#####

		self._detect_project_name()


		self._detect_person_name()


		self.find_sections()


		return self.INFORMATION
