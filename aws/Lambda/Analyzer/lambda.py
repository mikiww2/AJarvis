'''
list=[]

#0
list.append("Project name. Gucci ob. I'm Mario and yesterday i did nothing on the chair, but today i will work only at this project that i will complete the upload model. I'm having problems with the form but i'll finish it today")

#1
list.append("Project name. Gucci ob. Bacala. Tell me, europe titties. Yesterday, i did nothing on the chair, but today i will work only at this project that i will complete the upload, the eatem model so the user will be able to. I applaud the, uh, new content on the station, okay, are there any issues you know ? Well, is some trouble. We the forms. I tried to fix this thing, and how long is your tv ? Well, the the slow process is quite completed. A the only things. The only thing i am officially is the forum. Okay, thank you.")
list.append("Project name Gucci Hub, Nicola. tell me your activities. Yesterday i did nothing on the chart, today i will work only at this project and i will complete the uploder item model so the user will be able to upload a new content on this **. okay, are there any issues? no, well i've some trouble with forms and i will try to fix in this day. okay and how long is your activities? well, the upload process is quite complete, the only things the only thing i have to finish is the form. okay, thank you.")
list.append("Project name Gucci Hub, Nicola. tell me your activities. Yesterday i did nothing on the chart(***), today i will work only at this project and i will complete the uploder item model so the user will be able to upload a new content on this **. okay, are there any issues? no, well (eee) i've some trouble with forms and i will try to fix in this day. okay and (***) how long is your activities? well, the upload process is quite complete, the only things the only thing i have to finish is the form. okay, thank you.")

#2
list.append("Project name. Elite windows. Nicola tells me europe titties. Yesterday i eighteen, the decision form, so a user is forced to accept the terms and condition and privacy agreement on the region station, for instance. Now i'm raising for diego finisher is changes, so we can. They s o we can make the same changes. Are there any issues in your titties know ? And when you should, the complete the easy, okay.")
list.append("Project name Elite windows, Nicola tell me your activities. Yesterday i change the registration form, so now the user is force to accept the terms and conditions and privacy agreement on the registration forms. Now i'm waiting for Diego his changes so we can take so we can make the same changes. okay are there any issues in your activities ? No. And when you should complete this task? i hope this day. Okay")
list.append("Project name Elite windows, Nicola tell me your activities. Yesterday i change the registration form, so now the user is force to accept the terms and conditions and privacy agreement on the registration forms. Now i'm waiting for Diego his changes so we can take so we can make the same changes. okay are there any issues in your activities ? No. And when you should complete this task? i hope this day. Okay")

#3
list.append("project name good job tell me your activities yesterday I do nothing at this project and I will complete the uploader so that you will be able to upload a new Contender on this patient. okay I'm that I need shoes no LOL I had some trouble with the forms light fixture in this day and .how long is your. well quite complete. hey the only. things the only thing that gets finished is the form. okay thank you")
####

'''

if 's3' not in locals():

    from boto3 import client, resource
    from analyzer import Analyzer
    import logging, json
    
    logger=logging.getLogger()
    logger.setLevel(logging.INFO)

    s3=client('s3')
    dynamodb=resource('dynamodb')
    #comprehend=client('comprehend')
    
    standup_table=dynamodb.Table('violetto-Ajarvis-standups')

def lambda_handler(event, context):
    
    #retrieve json
    bucket_name=event['Records'][0]['s3']['bucket']['name']
    object_key=event['Records'][0]['s3']['object']['key']
    
    logger.info('bucket_name = %s', bucket_name)
    logger.info('object_key = %s', object_key)
    
    response=s3.get_object(
        Bucket=bucket_name,
        Key=object_key
    )
    
    transcribe_result=json.loads(response['Body'].read()) #.decode('utf-8')
    
    logger.info('transcribe_result = %s', json.dumps(transcribe_result))
    
    if 'standup' in transcribe_result:
        from_audio=False
        text=transcribe_result['standup']
        logger.info(text)
    elif 'results' in transcribe_result:
        from_audio=True
        if len(transcribe_result['results']['transcripts']):
            
            text=transcribe_result['results']['transcripts'][0]['transcript']
            logger.info('%s, text = %s', transcribe_result['status'], text)
            
            #formatting tokenized text, i don't need time and confidence
            
            items=transcribe_result['results']['items']
            
            for elem in items:
                '''
                "start_time":"1.750",
                "end_time":"2.230",
                "alternatives":
                [
                    {"confidence":"0.9997",
                    "content":"Project"}
                ],
                "type":"pronunciation"
                '''
                if 'start_time' in elem:
                    del elem['start_time']
                
                if 'end_time' in elem:
                    del elem['end_time']
                
                elem['token']=elem['alternatives'][0]['content']
                
                if len(elem['alternatives']) > 1:
                    del elem['alternatives'][0]
                
                    for alternative in elem['alternatives']:
                        alternative=alternative['content']
                else:
                    del elem['alternatives']
                
                del elem['type']
                        
                logger.info('Found token %s', elem)
                    
            
            logger.info('tokens created')
            logger.info(items)
                    
        else:
            logger.error('transcribe empty')
            text='empty'
    else:
        logger.error('cannot read %s', object_key)
        raise Exception('cannot read '+object_key)

    if not text or text == '' or text.isspace():
        logger.error('Text is empty, nothing to do')
        raise Exception('text empty')

#### ANALYZE TEXT
    analyzer=Analyzer()

    information=analyzer.analyze(text)

    logger.info(information)


#### UPDATE DYNAMO
    standupId=object_key[-24:-5]
    userId=object_key[7:-25]
    logger.info('standupId = %s, userId = %s', standupId, userId)

    expressionAttributeValues={}

    updateExpression='SET standupStatus = :status'
    expressionAttributeValues[':status']='COMPREHEND COMPLETED'

    updateExpression+=', transcribe = :text'
    expressionAttributeValues[':text']=text

    updateExpression+=', textSource = :source'
    if from_audio:
        expressionAttributeValues[':source']='audio'
    else:
        expressionAttributeValues[':source']='text'

    if 'PROJECT_NAME' in information:
        updateExpression+=', projectName = :project'
        expressionAttributeValues[':project']=information['PROJECT_NAME']
    else:
        logger.error('Cannot insert project name if absent')

    if 'PERSON_NAME' in information:
        updateExpression+=', personName = :person'
        expressionAttributeValues[':person']=information['PERSON_NAME']
    else:
        logger.error('Cannot insert person name if absent')

    if 'YESTERDAY' in information and information['YESTERDAY']:
        updateExpression+=', yesterdayInformations = :yInfo'
        expressionAttributeValues[':yInfo']=information['YESTERDAY']
    else:
        logger.error('Cannot insert yesterday if absent')

    if 'TODAY' in information and information['TODAY']:
        updateExpression+=', todayInformations = :tInfo'
        expressionAttributeValues[':tInfo']=information['TODAY']
    else:
        logger.error('Cannot insert today if absent')

    if 'ISSUE' in information and information['ISSUE']:
        updateExpression+=', issueInformations = :iInfo'
        expressionAttributeValues[':iInfo']=information['ISSUE']
    else:
        logger.error('Cannot insert issue if absent')

    if 'DURATION' in information and information['DURATION']:
        updateExpression+=', durationInformations = :dInfo'
        expressionAttributeValues[':dInfo']=information['DURATION']
    else:
        logger.error('Cannot insert duration if absent')


    logger.info('updateExpression : %s', updateExpression)
    logger.info('expressionAttributeValues : %s', expressionAttributeValues)

    standup_table.update_item(
        Key={
            'standupId': standupId,
            'userId': userId
        },
        UpdateExpression=updateExpression,
        ExpressionAttributeValues=expressionAttributeValues
    )
