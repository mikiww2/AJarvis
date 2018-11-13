if 'transcribe' not in locals():

    from boto3 import client, resource
    from boto3.dynamodb.conditions import Key, Attr
    from datetime import datetime, timedelta
    import logging, json
    import urllib.request
    
    bucket_name='violetto-stage'
    
    logger=logging.getLogger()
    logger.setLevel(logging.INFO)

    transcribe=client('transcribe')
    s3=client('s3')
    
    transcribe=client('transcribe')
    dynamodb=resource('dynamodb')
    jobs_table=dynamodb.Table('violetto-Ajarvis-transcription-jobs')
    standup_table=dynamodb.Table('violetto-Ajarvis-standups')

def lambda_handler(event, context):
    logger.info('scheduled event %s ', event['time'])
    
    scan_response=jobs_table.scan()

    items=scan_response['Items']
    
    if items:
        while True:
            if scan_response.get('LastEvaluatedKey'):
                last_key=scan_response['LastEvaluatedKey']
                scan_response=jobs_table.scan(ExclusiveStartKey=last_key)
                
                items+=scan_response['Items']
            else:
                break
        
        items=sorted(items, key=lambda item: item['jobName'])
        free_job=2
        queue_job=[]
        
        for item in items:
            jobName=item['jobName']
            
            logger.info('found transcribe job name %s', jobName)  #violetto-stage-AjarvisWebApp-admin-2018-03-02T10-31-06
            
            if len(item) == 1:
                try:
                    job_response=transcribe.get_transcription_job(TranscriptionJobName=jobName)
                    
                    TranscriptionJob=job_response['TranscriptionJob']
                    
                    if TranscriptionJob['TranscriptionJobStatus'] == 'IN_PROGRESS':
                        logger.info('%s still in progress', jobName)
                        free_job-=1
                        
                    else:
                        StandupDict={}
                        
                        list=jobName.split('-')
                        
                        StandupDict['standupId']=jobName[-19:]
                        
                        StandupDict['userId']=list[2]
                        
                        if len(list) == 9:
                            StandupDict['userId']+='/'+list[3]
                        
                        StandupDict['standupStatus']='VOICE-TO-TEXT '+TranscriptionJob['TranscriptionJobStatus']
                        
                        if TranscriptionJob['TranscriptionJobStatus'] == 'FAILED':
                            StandupDict['failureReason']=TranscriptionJob['FailureReason']
                            StandupDict['textSource']='audio'
                            
                        
                        if TranscriptionJob['TranscriptionJobStatus'] == 'COMPLETED':
                            workingTime=TranscriptionJob['CompletionTime']-TranscriptionJob['CreationTime']
                            
                            StandupDict['workingTime']=int(workingTime.total_seconds())
                        
                        logger.info('StandupItem = %s', json.dumps(StandupDict, sort_keys=True))
                        
                        
                        standup_table.put_item(
                           Item=StandupDict,
                           ConditionExpression='attribute_not_exists(standupId) and attribute_not_exists(userId)'
                        )
                        
                        logger.info('StandupItem saved on DynamoDB')
                        
                        if TranscriptionJob['TranscriptionJobStatus'] == 'COMPLETED':
                            #save json on bucket s3
                            
                            file_name='upload/'+StandupDict['userId']+'/'+StandupDict['standupId']+'.json'
                            
                            with urllib.request.urlopen(TranscriptionJob['Transcript']['TranscriptFileUri']) as f:
                                s3.upload_fileobj(f, bucket_name, file_name)
                                
                            logger.info('done saving %s on s3', file_name)
                        
                        jobs_table.delete_item(
                            Key={ 'jobName': jobName }
                        )
                        
                        logger.info('done deleting %s on dynamoDB', jobName)
                
                except Exception as e:
                    logger.error('error get transcribe jobs = %s', e)
                    
                    jobs_table.delete_item(
                        Key={ 'jobName': jobName }
                    )
                    logger.info('cannon find transcription job, deleted %s',jobName)
            
            else:
                logger.info('found transcribe job yet to start, add to queue')
                queue_job.append(item)
        
        logger.info('items done : %s', len(items)) 
        
        while free_job > 0 and len(queue_job):
            free_job-=1
            item=queue_job.pop(0)
            
            logger.info('found transcribe job yet to start, try starting')
               
            try:
                transcribe.start_transcription_job(
                    TranscriptionJobName=item['jobName'],
                    LanguageCode=item['languageCode'],
                    MediaSampleRateHertz=int(item['mediaSampleRateHertz']),
                    MediaFormat=item['mediaFormat'],
                    Media={ 'MediaFileUri': item['mediaFileUri'] }
                )
                
                logger.info('done creating transciption job, update table dynamoDB')
                
                jobs_table.update_item(
                    Key={ 'jobName': item['jobName'] },
                    UpdateExpression='REMOVE languageCode, mediaSampleRateHertz, mediaFormat, mediaFileUri'
                )
                
                logger.info('job started')
                
            except Exception as e:
                logger.error(e)
                logger.info('cannot create new transcription job, let for later')
    
    else:
        logger.info('no transcribe-job found')
    