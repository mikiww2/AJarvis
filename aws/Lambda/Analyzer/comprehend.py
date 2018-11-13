from boto3 import client
import logging, json

def dominant_language(text):
	comprehend=client('comprehend')

	response=comprehend.detect_dominant_language(Text=text)
	# { 'Languages': [ { 'LanguageCode': 'string', 'Score': ... } ] }

	###self.logger.info('Languages: %s', response['Languages'])
	return response['Languages'][0]['LanguageCode']

def entities(text, language='en'):
	comprehend=client('comprehend')

	response=comprehend.detect_entities(
		Text=text,
		LanguageCode=language #en | es
	)
	#{ 'Entities': [ {
	#    'Score': ...,
	#    'Type': 'PERSON'|'LOCATION'|'ORGANIZATION'|'COMMERCIAL_ITEM'|'EVENT'|'DATE'|'QUANTITY'|'TITLE'|'OTHER',
	#    'Text': 'string',
	#    'BeginOffset': 123,
	#    'EndOffset': 123
	#} ] }

	###self.logger.info('Entities: %s', response['Entities'])

	array=[]
	for elem in response['Entities']:
		array.append({ "Type" : elem['Type'], "Text" : elem['Text'] })

	return array

def key_phrases(text, language='en'):
	comprehend=client('comprehend')

	response=comprehend.detect_key_phrases(
		Text=text,
		LanguageCode=language #en | es
	)
	#{ 'KeyPhrases': [ {
	#    'Score': ...,
	#    'Text': 'string',
	#    'BeginOffset': 123,
	#    'EndOffset': 123
	#} ] }

	###self.logger.info('KeyPhrases: %s', response['KeyPhrases'])

	array=[]
	for elem in response['KeyPhrases']:
		array.append(elem['Text'])

	return array

def sentiment(text, language='en'):
	comprehend=client('comprehend')

	response=comprehend.detect_sentiment(
		Text=text,
		LanguageCode=language #en | es
	)
	#{ 'Sentiment': 'POSITIVE'|'NEGATIVE'|'NEUTRAL'|'MIXED',
	#  'SentimentScore': {
	#    'Positive': ...,
	#    'Negative': ...,
	#    'Neutral': ...,
	#    'Mixed': ...
	#} }

	###self.logger.info('Sentiment: %s', response['Sentiment'])
	return { "Sentiment": response['Sentiment'], "SentimentScore": response['SentimentScore'] }
