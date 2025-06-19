import json
import boto3
import uuid
import os
from datetime import datetime
from botocore.exceptions import ClientError

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])

def lambda_handler(event, context):
    """
    Lambda function handler for API Gateway POST requests.
    Processes incoming data and stores it in DynamoDB.
    """
    try:
        # Parse the request body
        if 'body' not in event:
            return create_response(400, {'error': 'Request body is required'})
        
        # Parse JSON body
        try:
            body = json.loads(event['body'])
        except json.JSONDecodeError:
            return create_response(400, {'error': 'Invalid JSON in request body'})
        
        # Validate required fields (customize based on your needs)
        if not body:
            return create_response(400, {'error': 'Request body cannot be empty'})
        
        # Generate a unique ID for the record
        record_id = str(uuid.uuid4())
        
        # Prepare the item for DynamoDB
        item = {
            'id': record_id,
            'data': body,
            'created_at': datetime.utcnow().isoformat(),
            'source': 'api_gateway'
        }
        
        # Add any additional processing here based on your requirements
        # For example, you might want to:
        # - Validate specific fields
        # - Transform data
        # - Add business logic
        # - Call external services
        
        # Insert the item into DynamoDB
        table.put_item(Item=item)
        
        # Return success response
        return create_response(200, {
            'message': 'Data successfully stored',
            'id': record_id,
            'data': body
        })
        
    except ClientError as e:
        print(f"DynamoDB error: {e}")
        return create_response(500, {'error': 'Database operation failed'})
    except Exception as e:
        print(f"Unexpected error: {e}")
        return create_response(500, {'error': 'Internal server error'})

def create_response(status_code, body):
    """
    Create a properly formatted API Gateway response.
    """
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'POST, OPTIONS'
        },
        'body': json.dumps(body)
    } 