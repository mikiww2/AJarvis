if 's3' not in locals():

  from boto3 import client
  from datetime import datetime
  import logging, json
  
  logger=logging.getLogger()
  logger.setLevel(logging.INFO)

  s3=client('s3')
  bucket_name='violetto-stage'

def lambda_handler(event, context): # event contain http get /upload/ request, context contain info of lambda enviroment

  #retrieve information
  d=datetime.now()
  logger.info('now = %s', d)
  
  user=event['requestContext']['authorizer']['principalId']
  logger.info('user %s', user)
   
  '''
  key='upload/'+user+'/'+str(d.year)
  
  if d.month < 10:
    key+='/0'+str(d.month)
  else:
    key+='/'+str(d.month)

  if d.day < 10:
    key+='/0'+str(d.day)
  else:
    key+='/'+str(d.day)
    
  if event['headers']['sub-user']:
    key+='/'+event['headers']['sub-user']
  
  key+='/'+d.strftime('%Y-%m-%dT%H-%M-%S')+'.wav'
  '''
  
  key='upload/'+user
  
  logger.info(event['headers'])
  if 'sub-user' in event['headers']:
    key+='/'+event['headers']['sub-user']
    
  key+='/'+d.strftime('%Y-%m-%dT%H-%M-%S')+'.wav'
  logger.info('key = %s', key)
  
  #generate url
  presigned_url=s3.generate_presigned_url(
    ClientMethod='put_object',
    Params={
      'Bucket': bucket_name,
      'Key': key,
      'ContentType': 'audio/wav'
    }
  )
  
  logger.warn('presigned_url = %s', presigned_url)
  
  payload={ 'upload_url': presigned_url }

  return {
    'isBase64Encoded': False,
    'statusCode': 200,
    'headers': {
      'Content-Type':'application/json',
      'Access-Control-Allow-Origin': '*'
    },
    'body': json.dumps(payload)
  }
