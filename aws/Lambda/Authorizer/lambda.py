if 'dynamoDB' not in locals():
    
    from boto3 import resource
    from hashlib import sha224
    from base64 import standard_b64decode
    import logging
    
    logger=logging.getLogger()
    logger.setLevel(logging.INFO)
    
    dynamodb=resource('dynamodb')
    users_table=dynamodb.Table('violetto-Ajarvis-users')
    
def lambda_handler(event, context):
    
    logger.info('Client Token: %s', event['authorizationToken'])
    logger.info('Method ARN: %s', event['methodArn'])
    
    #get token
    token=event['authorizationToken']

    #check isBasicHttpAuth
    if not token.startswith('Basic '):
        logger.warn('Incorrect authentication - not Basic')
        raise Exception('Unauthorized') # return 401
        
    #check username:password
    token=token[6:] #remove "Basic "
    auth_info=standard_b64decode(token).decode("utf-8").split(":", 1)
    
    if len(auth_info) != 2:
        logger.warn('Incomplete basic authentication - no username/password')
        raise Exception('Unauthorized') # return 401
    
    username=auth_info[0]
    password=auth_info[1]
    
    #check users
    response = users_table.get_item( Key={ 'userId': username } )
    
    # not found user
    if 'Item' not in response:
        logger.info('Username %s not in DynamoDB', username)
        raise Exception('Unauthorized') # return 401
    
    # wrong password
    hash_password=sha224(password.encode('utf-8')).hexdigest()
    if response['Item']['password'] != hash_password:
        logger.info('Password for username %s with password %s, %s != %s', username, password, response['Item']['password'], hash_password)
        raise Exception('Unauthorized') # return 401
    
    logger.warn('Allow %s login', response['Item']['name'])

    # allow to login
    return {
        'principalId': response['Item']['name'],
        'policyDocument': {
            'Version': '2012-10-17',
            'Statement': [{
                'Action': 'execute-api:Invoke',
                'Effect': 'Allow',
                'Resource': event['methodArn']
            }]
        }
    }