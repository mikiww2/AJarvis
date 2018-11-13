if 'transcribe' not in locals():

    from boto3 import client, resource
    from datetime import datetime
    import logging
    
    url_s3='https://s3-us-east-1.amazonaws.com'
    
    logger=logging.getLogger()
    logger.setLevel(logging.INFO)

    transcribe=client('transcribe')
    dynamodb=resource('dynamodb')
    
    jobs_table=dynamodb.Table('violetto-Ajarvis-transcription-jobs')

def lambda_handler(event, context): # event contain http get /upload/ request, context contain info of lambda enviroment

    bucket=url_s3+'/'+event['Records'][0]['s3']['bucket']['name']
    object=event['Records'][0]['s3']['object']['key']
    
    url_object=bucket+'/'+object
    logger.info('url_object = %s', url_object)
    
    job_name='violetto-stage-'+object[7:-4].replace('/','-')
    logger.info('job_name = %s', job_name)
    
    try:
        transcribe.start_transcription_job( #ignore response ?
            TranscriptionJobName=job_name,
            LanguageCode='en-US',
            MediaSampleRateHertz=44100, #check on rec.js api.... 44000 there but is 44100 when file is saved
            MediaFormat='wav',
            Media={ 'MediaFileUri': url_object }
        )
        
        try:
            jobs_table.put_item(
                Item={
                    'jobName': job_name
                },
                ConditionExpression='attribute_not_exists(jobName)'
            )
        except Exception as e:
            logger.error('error there is another transcribe jobs item with jobName = %s', job_name)
            logger.info(e)
            raise Exception
        
        logger.info('job started')
    except Exception as e:
        logger.error(e)
        logger.info('cannot create new transcription job, save in dynamoDB for later')
        try:
            jobs_table.put_item(
                Item={
                    'jobName': job_name,
                    'languageCode':'en-US',
                    'mediaSampleRateHertz':44100,
                    'mediaFormat':'wav',
                    'mediaFileUri': url_object
                    
                },
                ConditionExpression='attribute_not_exists(jobName)'
            )
        except Exception as e:
            logger.error('error there is another transcribe jobs item with jobName = %s', job_name)
            logger.info(e)
            raise Exception
        
        logger.info('job saved')