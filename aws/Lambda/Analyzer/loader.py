from boto3 import client
import json


def load_tokens(bucket_name='violetto-stage', object_key='comprehend/tokens.json'):
	s3=client('s3')

	response=s3.get_object(
		Bucket=bucket_name,
		Key=object_key
	)

	return json.loads(response['Body'].read()) #.decode('utf-8')

def load_helper(bucket_name='violetto-stage', object_key='comprehend/helper.json'):
	s3=client('s3')

	try:
		response=s3.get_object(
			Bucket=bucket_name,
			Key=object_key
		)

		return json.loads(response['Body'].read()) #.decode('utf-8')

	except Exception:
		return None

'''
def load_ignore_tokens(bucket_name='violetto-stage', object_key='comprehend/ignore_tokens.json'):
	s3=client('s3')

	try:
		response=s3.get_object(
			Bucket=bucket_name,
			Key=object_key
		)

		return json.loads(response['Body'].read())['ignore_tokens'] #.decode('utf-8')

	except Exception:
		return None
'''
def load_ignore_tags(bucket_name='violetto-stage', object_key='comprehend/ignore_tags.json'):
	s3=client('s3')

	try:
		response=s3.get_object(
			Bucket=bucket_name,
			Key=object_key
		)

		return json.loads(response['Body'].read()) #.decode('utf-8')

	except Exception:
		return None

'''

def load_tokens(bucket_name='violetto-stage', object_key='comprehend/tokens.json'):
	with open("tokens.json") as file:
		tokens = json.loads(file.read())

	return tokens

def load_helper(bucket_name='violetto-stage', object_key='comprehend/helper.json'):
	try:
		with open("helper.json") as file:
			helper = json.loads(file.read())

		return helper

	except Exception:
		return None
'''
'''
def load_ignore_tokens(bucket_name='violetto-stage', object_key='comprehend/ignore_tokens.json'):
	try:
		with open("ignore_tokens.json") as file:
			ignore_tokens = json.loads(file.read())

		return ignore_tokens['ignore_tokens'] #.decode('utf-8')

	except Exception:
		return None
'''