import json
import boto3
from botocore.exceptions import ClientError
from decimal import Decimal
from boto3.dynamodb.conditions import Key

# Initialize the DynamoDB client
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
dynamodb_table = dynamodb.Table('product-inventory')

status_check_path = '/health'
productPath = '/product'
productsPath = '/products'

getMethod = 'GET'
postMethod = 'POST'
patchMethod = 'PATCH'
deleteMethod = 'DELETE'

def lambda_handler(event, context):
    print('Request event: ', event)
    response = None
   
    try:
        httpMethod = event.get('httpMethod')
        path = event.get('path')

        if httpMethod == getMethod and path == status_check_path:
            response = build_response(200, 'Service is operational')
        elif httpMethod == getMethod and path == productPath:
            product_id = event['queryStringParameters']['productid']
            response = get_product(product_id)
        elif httpMethod == getMethod and path == productsPath:
            response = get_products()
        elif httpMethod == postMethod and path == productPath:
            response = save_product(json.loads(event['body']))
        elif httpMethod == patchMethod and path == productPath:
            body = json.loads(event['body'])
            response = modify_product(body['productId'], body['updateKey'], body['updateValue'])
        elif httpMethod == deleteMethod and path == productPath:
            body = json.loads(event['body'])
            response = delete_product(body['productId'])
        else:
            response = build_response(404, '404 Not Found')

    except Exception as e:
        print('Error:', e)
        response = build_response(400, 'Error processing request')
   
    return response

def get_product(product_id):
    try:
        response = dynamodb_table.get_item(Key={'productid': product_id})
        return build_response(200, response.get('Item'))
    except ClientError as e:
        print('Error:', e)
        return build_response(400, e.response['Error']['Message'])

def get_products():
    try:
        scan_params = {
            'TableName': dynamodb_table.name
        }
        return build_response(200, scan_dynamo_records(scan_params, []))
    except ClientError as e:
        print('Error:', e)
        return build_response(400, e.response['Error']['Message'])

def scan_dynamo_records(scan_params, item_array):
    response = dynamodb_table.scan(**scan_params)
    item_array.extend(response.get('Items', []))
   
    if 'LastEvaluatedKey' in response:
        scan_params['ExclusiveStartKey'] = response['LastEvaluatedKey']
        return scan_dynamo_records(scan_params, item_array)
    else:
        return {'products': item_array}

def save_product(request_body):
    try:
        dynamodb_table.put_item(Item=request_body)
        body = {
            'Operation': 'SAVE',
            'Message': 'SUCCESS',
            'Item': request_body
        }
        return build_response(200, body)
    except ClientError as e:
        print('Error:', e)
        return build_response(400, e.response['Error']['Message'])

def modify_product(product_id, update_key, update_value):
    try:
        response = dynamodb_table.update_item(
            Key={'productid': product_id},
            UpdateExpression=f'SET {update_key} = :value',
            ExpressionAttributeValues={':value': update_value},
            ReturnValues='UPDATED_NEW'
        )
        body = {
            'Operation': 'UPDATE',
            'Message': 'SUCCESS',
            'UpdatedAttributes': response
        }
        return build_response(200, body)
    except ClientError as e:
        print('Error:', e)
        return build_response(400, e.response['Error']['Message'])

def delete_product(product_id):
    try:
        response = dynamodb_table.delete_item(
            Key={'productid': product_id},
            ReturnValues='ALL_OLD'
        )
        body = {
            'Operation': 'DELETE',
            'Message': 'SUCCESS',
            'Item': response
        }
        return build_response(200, body)
    except ClientError as e:
        print('Error:', e)
        return build_response(400, e.response['Error']['Message'])

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            # Check if it's an int or a float
            if obj % 1 == 0:
                return int(obj)
            else:
                return float(obj)
        # Let the base class default method raise the TypeError
        return super(DecimalEncoder, self).default(obj)

def build_response(status_code, body):
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': json.dumps(body, cls=DecimalEncoder)
    }