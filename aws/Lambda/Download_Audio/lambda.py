if 's3' not in locals():
    from boto3 import client
    from datetime import datetime
    import logging, json
    
    logger=logging.getLogger()
    logger.setLevel(logging.INFO)
    
    s3=client('s3')
    bucket_name='violetto-stage'

def lambda_handler(event, context): # event contain http get /upload/ request, context contain info of lambda enviroment
    
    user=event['requestContext']['authorizer']['principalId']
    logger.info('user %s', user)
    
    key='upload/'+user
    
    logger.info(event['headers'])
    if 'sub-user' in event['headers']:
        key+='/'+event['headers']['sub-user']
    
    if 'pathParameters' not in event or 'standupId' not in event['pathParameters']:
        logger.error("download audio without standup id")
        return {
            'isBase64Encoded': False,
            'statusCode': 400,
            'headers': {
              'Content-Type':'application/json',
              'Access-Control-Allow-Origin': '*'
            },
            'body': { 'message': 'Download audio without standupId' }
        }
    
    standupId=event['pathParameters']['standupId']
    logger.info('standupId = %s', standupId)
    try:
        datetime.strptime(standupId, '%Y-%m-%dT%H-%M-%S')
    except ValueError as e:
        logger.error(e)
        return {
            'isBase64Encoded': False,
            'statusCode': 400,
            'headers': {
              'Content-Type':'application/json',
              'Access-Control-Allow-Origin': '*'
            },
            'body': { 'message': 'Bad standupId' }
        }
        
    key+='/'+standupId+'.wav'
    #generate url
    presigned_url=s3.generate_presigned_url(
        ClientMethod='get_object',
            Params={
              'Bucket': bucket_name,
              'Key': key
            }
        )
    
    logger.warn('presigned_url = %s', presigned_url)
    
    payload={ 'download_url': presigned_url }
    
    return {
        'isBase64Encoded': False,
        'statusCode': 200,
        'headers': {
          'Content-Type':'application/json',
          'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(payload)
    }
