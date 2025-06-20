"""
DynamoDB operations module for storing processed data.
"""

import json
import boto3
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from botocore.exceptions import ClientError


class DynamoDBManager:
    """Manages DynamoDB operations for data storage."""
    
    def __init__(self, table_name: str):
        self.table_name = table_name
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table(table_name)
    
    def store_processed_data(self, data: Dict[str, Any], record_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Store processed data in DynamoDB.
        
        Args:
            data: Processed data to store
            record_id: Optional record ID (will generate if not provided)
            
        Returns:
            Dict with operation result
        """
        try:
            if not record_id:
                record_id = str(uuid.uuid4())
            
            # Prepare item for DynamoDB
            item = {
                'id': record_id,
                'data': data,
                'created_at': datetime.utcnow().isoformat(),
                'source': 'lambda_processor',
                'version': '1.0'
            }
            
            # Add metadata
            if 'metadata' in data:
                item['metadata'] = data['metadata']
            
            # Add summary if available
            if 'summary' in data:
                item['summary'] = data['summary']
            
            # Store in DynamoDB
            self.table.put_item(Item=item)
            
            return {
                'status': 'success',
                'record_id': record_id,
                'table_name': self.table_name,
                'timestamp': datetime.utcnow().isoformat(),
                'item_size': len(json.dumps(item))
            }
            
        except ClientError as e:
            return {
                'status': 'error',
                'error': str(e),
                'error_code': e.response['Error']['Code'],
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }

def store_data(table_name: str, data: Dict[str, Any], record_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Convenience function to store data in DynamoDB.
    
    Args:
        table_name: DynamoDB table name
        data: Data to store
        record_id: Optional record ID
        
    Returns:
        Dict with operation result
    """
    db_manager = DynamoDBManager(table_name)
    return db_manager.store_processed_data(data, record_id) 