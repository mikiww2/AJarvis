if 'logger' not in locals():
    
    from boto3 import client, resource
    from boto3.dynamodb.conditions import Key, Attr
    from datetime import datetime
    import logging, json
    
    logger=logging.getLogger()
    logger.setLevel(logging.INFO)
    
    dynamodb=resource('dynamodb')
    standup_table=dynamodb.Table('violetto-Ajarvis-standups')
    
    range_values=['ALL', 'DAY', 'ONE']

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
        
#### VALIDATE BODY
    logger.info('body = %s', event['body'])
    body=json.loads(event['body'])
    
    if 'show' not in body:
        logger.error('invalid body, miss show')
        
        message='Request standup with invalid body, need show'
        return {
            'isBase64Encoded': False,
            'statusCode': 400,
            'headers': {
              'Content-Type':'application/json',
              'Access-Control-Allow-Origin': '*'
            },
            'body': { 'message': message }
        }
    
    show=body['show']
    logger.info('show = %s', ', '.join(show))
    
    #default standupId always present
    projection='standupId, textSource'
    
    if 'text' in show:
        projection+=',transcribe'
    if 'status' in show:
        projection+=',standupStatus'
    if 'project' in show:
        projection+=',projectName'
    if 'person' in show:
        projection+=',personName'
    if 'yesterday' in show:
        projection+=',yesterdayInformations'
    if 'today' in show:
        projection+=',todayInformations'
    if 'issue' in show:
        projection+=',issueInformations'
    if 'duration' in show:
        projection+=',durationInformations'
    #if '' in show:
    #    projection+=','
    
    logger.info('projection = %s', projection)
    
    if 'pathParameters' not in event or not event['pathParameters'] or 'range' not in event['pathParameters']: #retrieve without range
        logger.info('call retrieve, range set to ONE')
        range='ONE'
    else:
        range=event['pathParameters']['range']
        logger.info('range = %s', range)
    
    if range == 'ONE':
        if 'id' not in body:
            logger.error('invalid body, miss id')
            
            message='Request standup with invalid body, need id'
            return {
                'isBase64Encoded': False,
                'statusCode': 400,
                'headers': {
                  'Content-Type':'application/json',
                  'Access-Control-Allow-Origin': '*'
                },
                'body': { 'message': message }
            }
        
        standupId=body['id']
        logger.info('standupId =%s', standupId)
        
        try:
            datetime.strptime(standupId, '%Y-%m-%dT%H-%M-%S')
        except ValueError:
            logger.error("Incorrect standupId format")
            return {
                'isBase64Encoded': False,
                'statusCode': 400,
                'headers': {
                  'Content-Type':'application/json',
                  'Access-Control-Allow-Origin': '*'
                },
                'body': { 'message': 'invalid standupId, should be %Y-%m-%dT%H-%M-%S' }
            }
    
    elif range == 'DAY':
        if 'date' not in body:
            logger.error('invalid body, miss date')
            
            message='Request standup with invalid body, need date'
            return {
                'isBase64Encoded': False,
                'statusCode': 400,
                'headers': {
                  'Content-Type':'application/json',
                  'Access-Control-Allow-Origin': '*'
                },
                'body': { 'message': message }
            }
        
        choose_date=body['date']
        logger.info('date =%s', choose_date)
        
        try:
            choose_date=datedatetime.strptime(choose_date, '%Y-%m-%d')
        except ValueError:
            logger.error("Incorrect choose_date format")
            return {
                'isBase64Encoded': False,
                'statusCode': 400,
                'headers': {
                  'Content-Type':'application/json',
                  'Access-Control-Allow-Origin': '*'
                },
                'body': { 'message': 'invalid date, should be %Y-%m-%d' }
            }
    
    elif range == 'ALL':
        pass
        
    #elif range == '':
    #    pass
        
    else:
        logger.warn('Range = %s not valid', range)
        
        message='Request standup with invalid range = '+range
        message+='\n'
        message+='valid values are '+', '.join(range_values)
        return {
            'isBase64Encoded': False,
            'statusCode': 400,
            'headers': {
              'Content-Type':'application/json',
              'Access-Control-Allow-Origin': '*'
            },
            'body': {
                'message': message }
        }

#### RETRIEVE FROM DYNAMODB
    items=[]

    if range == 'ONE':
        response=standup_table.get_item(
            Key={
                'standupId': standupId,
                'userId': userId
            },
            ProjectionExpression=projection
        )
        
        if not response or 'Item' not in response:
            logger.error('standup not found')
            return {
                'isBase64Encoded': False,
                'statusCode': 400,
                'headers': {
                  'Content-Type':'application/json',
                  'Access-Control-Allow-Origin': '*'
                },
                'body': { 'message': 'cannot find standup' }
            }
        else:
            items.append(response['Item'])
    else:
        if range == 'ALL':
            response=standup_table.scan(
                FilterExpression=Key('userId').begins_with(userId),
                ProjectionExpression=projection
            )
        else:
            query_condition=condition
            if range == 'ONE':
                query_condition=query_condition & Key('standupId').eq(standupId)
                
            elif range == 'DAY':
                query_condition=query_condition & Key('standupId').begins_with(choose_date)
            #add more condition here
            
            response=standup_table.query(
                KeyConditionExpression=query_condition,
                ProjectionExpression=projection
            )
            
        items=response['Items']
        
        if items:
            while True:
                if response.get('LastEvaluatedKey'):
                    last_key=response['LastEvaluatedKey']
                    
                    if range != 'ALL':
                        response=standup_table.query(
                            KeyConditionExpression=query_condition,
                            ProjectionExpression=projection,
                            ExclusiveStartKey=last_key
                        )
                    else:
                        response=standup_table.scan(
                            FilterExpression=key('userId').begins_with(userId),
                            ProjectionExpression=projection,
                            ExclusiveStartKey=last_key
                        )
                        
                    items+=response['Items']
                else:
                    break
    logger.info('items = %s', items)
        
    for item in items:
        logger.info('raw item = %s', item)
        
        item['id']=item['standupId']
        del item['standupId']
        
        item['source']=item['textSource']
        del item['textSource']
        
        if 'status' in show:
            item['status']=item['standupStatus']
            del item['standupStatus']
        
        if 'text' in show and 'transcribe' in item:
            item['text']=item['transcribe']
            del item['transcribe']
        
        if 'project' in show and 'projectName' in item:
            item['project']=item['projectName']
            del item['projectName']
        
        if 'person' in show and 'personName' in item:
            item['person']=item['personName']
            del item['personName']
            
        if 'yesterday' in show and 'yesterdayInformations' in item:
            item['yesterday']=item['yesterdayInformations']
            del item['yesterdayInformations']
        if 'today' in show and 'todayInformations' in item:
            item['today']=item['todayInformations']
            del item['todayInformations']
        if 'issue' in show and 'issueInformations' in item:
            item['issue']=item['issueInformations']
            del item['issueInformations']
        if 'duration' in show and 'durationInformations' in item:
            item['duration']=item['durationInformations']
            del item['durationInformations']
        #if '' in show:
        #    item['']=item['']
        #    del item['']
        logger.info('item = %s', item)
    
    #sort standupId
    if len(items) > 1:
        items=sorted(items, key=lambda item: item['id'], reverse=True)
    
    payload={ 'items': items }
        
    return {
        'isBase64Encoded': False,
        'statusCode': 200,
        'headers': {
          'Content-Type':'application/json',
          'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(payload)
      }