if 'logger' not in locals():
    from boto3 import client, resource
    from boto3.dynamodb.conditions import Key, Attr
    from datetime import datetime
    import logging, json
    
    logger=logging.getLogger()
    logger.setLevel(logging.INFO)
    
    dynamodb=resource('dynamodb')
    standup_table=dynamodb.Table('violetto-Ajarvis-standups')

def lambda_handler(event, context):
    #     "resource": "Resource path",
    #     "path": "Path parameter",
    #     "httpMethod": "Incoming request's method name"
    #     "headers": {Incoming request headers}
    #     "queryStringParameters": {query string parameters }
    #     "pathParameters":  {path parameters}
    #     "stageVariables": {Applicable stage variables}
    #     "requestContext": {Request context, including authorizer-returned key-value pairs}
    #     "body": "A JSON string of the request payload."
    #     "isBase64Encoded": "A boolean flag to indicate if the applicable request payload is Base64-encode"
    logger.info(event)
    
    user=event['requestContext']['authorizer']['principalId']
    logger.info('User = %s', user)
    
    if 'sub-user' in event['headers']:
        sub_user=event['headers']['sub-user']
        logger.info('Sub-user = %s', sub_user)
    else:
        sub_user=None
        logger.warn('Sub-user not found, ignoring subfoldering feature')

    userId=user
    if sub_user:
        userId+='/'+sub_user
    
    project_name=None
    
    if 'pathParameters' in event and event['pathParameters'] and 'project_name' in event['pathParameters']:
        project_name=event['pathParameters']['project_name']
        logger.info('project_name = %s', project_name)
        
    
#### RETRIEVE FROM DYNAMODB
    items=[]
    
    projection='standupId, transcribe, projectName, personName, yesterdayInformations, todayInformations, issueInformations, durationInformations'

    if not project_name:
        filterExpression=Key('userId').begins_with(userId) & Attr('standupStatus').eq('COMPREHEND COMPLETED') & Attr('projectName').exists()
        
        response=standup_table.scan(
            FilterExpression=filterExpression,
            ProjectionExpression=projection
        )
            
        items=response['Items']
        
        if items:
            while True:
                if response.get('LastEvaluatedKey'):
                    last_key=response['LastEvaluatedKey']
                    
                    response=standup_table.scan(
                        FilterExpression=filterExpression,
                        ProjectionExpression=projection,
                        ExclusiveStartKey=last_key
                    )
                        
                    items+=response['Items']
                else:
                    break

    logger.info('items = %s', items)
    
    projects=[]
    
    if not items and not project_name:
        payload={ 'projects': projects }
        
        return {
            'isBase64Encoded': False,
            'statusCode': 200,
            'headers': {
              'Content-Type':'application/json',
              'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(payload)
          }
    else:
        p={}
        
        for item in items:
            
            standup={}
            standup['id']=item['standupId']
            #standup['text']=item['transcribe']
            
            if 'personName' in item:
                standup['person']=item['personName']
                
            if 'yesterdayInformations' in item:
                for elem in item['yesterdayInformations']:
                    del elem['sentence']
                standup['yesterday']=item['yesterdayInformations']
                
            if 'todayInformations' in item:
                for elem in item['todayInformations']:
                    del elem['sentence']
                standup['today']=item['todayInformations']
                
            if 'issueInformations' in item:
                for elem in item['issueInformations']:
                    del elem['sentence']
                standup['issue']=item['issueInformations']
                
            if 'durationInformations' in item:
                for elem in item['durationInformations']:
                    del elem['sentence']
                standup['duration']=item['durationInformations']
            
            p_name=item['projectName']
                
            if p_name not in p.keys():
                p[p_name]=[]
                
            p[p_name].append(standup)
        
                
    #sort project standups
    if p:
        for key in p.keys():
            if len(p[key]) > 1:
                p[key]=sorted(p[key], key=lambda item: item['id'], reverse=True)
    
    items=[]
    for key in p.keys():
        items.append({ 'name': key, 'standups': p[key]})
    
    if items:
        items=sorted(items, key=lambda item:item['standups'][0]['id'], reverse=True)
    
    payload={ 'projects': items }
        
    return {
        'isBase64Encoded': False,
        'statusCode': 200,
        'headers': {
          'Content-Type':'application/json',
          'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(payload)
      }
        
                
            
