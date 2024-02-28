import boto3
import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodbTableName = 'product-inventory'
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(dynamodbTableName)

getMethod = 'GET'
postMethod = 'POST'
patchMethod = 'PATCH'
deleteMethod = 'DELETE'

healthPath = '/health'
productPath = '/product'
productsPath = '/products'

def buildResponse(statusCode, body=None):
    response = {
        'statusCode' : statusCode,
        'headers' : {
            'Content-Type' : 'application/json',
            'Access-Control-Allow-Origin' : '*'
        }
    }
    
    if body is not None:
        response['body'] = json.dumps(body)

def lambda_handler (event, context):
    logger.info(event)
    httpMethod = event['httpMethod']
    endpointPath = event['path']
    
    if httpMethod == getMethod and endpointPath == healthPath:
        response = buildResponse(200)






















