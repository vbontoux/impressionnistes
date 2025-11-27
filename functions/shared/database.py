"""
Database utilities for DynamoDB operations
Provides helper functions for common database operations
"""
import os
import boto3
import logging
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
from decimal import Decimal
from datetime import datetime

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class DatabaseClient:
    """
    DynamoDB client with helper methods for common operations
    """
    
    def __init__(self, table_name=None):
        """
        Initialize database client
        
        Args:
            table_name: DynamoDB table name (defaults to TABLE_NAME env var)
        """
        self.dynamodb = boto3.resource('dynamodb')
        self.table_name = table_name or os.environ.get('TABLE_NAME', 'impressionnistes-registration-dev')
        self.table = self.dynamodb.Table(self.table_name)
        logger.info(f"DatabaseClient initialized with table: {self.table_name}")
    
    def get_item(self, pk, sk):
        """
        Get a single item from DynamoDB
        
        Args:
            pk: Partition key value
            sk: Sort key value
            
        Returns:
            dict: Item or None if not found
        """
        try:
            response = self.table.get_item(
                Key={'PK': pk, 'SK': sk}
            )
            return response.get('Item')
        except ClientError as e:
            logger.error(f"Error getting item {pk}#{sk}: {e}")
            raise
    
    def put_item(self, item, condition_expression=None):
        """
        Put an item into DynamoDB
        
        Args:
            item: Item to put
            condition_expression: Optional condition expression
            
        Returns:
            dict: Response from DynamoDB
        """
        try:
            kwargs = {'Item': item}
            if condition_expression:
                kwargs['ConditionExpression'] = condition_expression
            
            response = self.table.put_item(**kwargs)
            logger.info(f"Put item: {item.get('PK')}#{item.get('SK')}")
            return response
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                logger.warning(f"Condition failed for put_item: {item.get('PK')}#{item.get('SK')}")
            else:
                logger.error(f"Error putting item: {e}")
            raise
    
    def update_item(self, pk, sk, updates, condition_expression=None):
        """
        Update an item in DynamoDB
        
        Args:
            pk: Partition key value
            sk: Sort key value
            updates: Dictionary of fields to update
            condition_expression: Optional condition expression
            
        Returns:
            dict: Updated item
        """
        # Build update expression
        update_expression_parts = []
        expression_attribute_names = {}
        expression_attribute_values = {}
        
        for key, value in updates.items():
            attr_name = f'#{key}'
            attr_value = f':{key}'
            update_expression_parts.append(f'{attr_name} = {attr_value}')
            expression_attribute_names[attr_name] = key
            expression_attribute_values[attr_value] = value
        
        try:
            kwargs = {
                'Key': {'PK': pk, 'SK': sk},
                'UpdateExpression': 'SET ' + ', '.join(update_expression_parts),
                'ExpressionAttributeNames': expression_attribute_names,
                'ExpressionAttributeValues': expression_attribute_values,
                'ReturnValues': 'ALL_NEW'
            }
            
            if condition_expression:
                kwargs['ConditionExpression'] = condition_expression
            
            response = self.table.update_item(**kwargs)
            logger.info(f"Updated item: {pk}#{sk}")
            return response['Attributes']
        except ClientError as e:
            logger.error(f"Error updating item {pk}#{sk}: {e}")
            raise
    
    def delete_item(self, pk, sk, condition_expression=None):
        """
        Delete an item from DynamoDB
        
        Args:
            pk: Partition key value
            sk: Sort key value
            condition_expression: Optional condition expression
            
        Returns:
            dict: Response from DynamoDB
        """
        try:
            kwargs = {'Key': {'PK': pk, 'SK': sk}}
            if condition_expression:
                kwargs['ConditionExpression'] = condition_expression
            
            response = self.table.delete_item(**kwargs)
            logger.info(f"Deleted item: {pk}#{sk}")
            return response
        except ClientError as e:
            logger.error(f"Error deleting item {pk}#{sk}: {e}")
            raise
    
    def query_by_pk(self, pk, sk_prefix=None, limit=None, scan_forward=True):
        """
        Query items by partition key
        
        Args:
            pk: Partition key value
            sk_prefix: Optional sort key prefix to filter
            limit: Maximum number of items to return
            scan_forward: Sort order (True for ascending, False for descending)
            
        Returns:
            list: List of items
        """
        try:
            kwargs = {
                'KeyConditionExpression': Key('PK').eq(pk),
                'ScanIndexForward': scan_forward
            }
            
            if sk_prefix:
                kwargs['KeyConditionExpression'] &= Key('SK').begins_with(sk_prefix)
            
            if limit:
                kwargs['Limit'] = limit
            
            response = self.table.query(**kwargs)
            items = response.get('Items', [])
            
            # Handle pagination if needed
            while 'LastEvaluatedKey' in response and (not limit or len(items) < limit):
                kwargs['ExclusiveStartKey'] = response['LastEvaluatedKey']
                response = self.table.query(**kwargs)
                items.extend(response.get('Items', []))
            
            logger.info(f"Queried {len(items)} items for PK={pk}")
            return items
        except ClientError as e:
            logger.error(f"Error querying items for PK={pk}: {e}")
            raise
    
    def query_gsi(self, index_name, pk_value, sk_value=None, limit=None, pk_attr_name=None, sk_attr_name=None):
        """
        Query items using a Global Secondary Index
        
        Args:
            index_name: Name of the GSI (GSI1, GSI2, GSI3)
            pk_value: Partition key value for the GSI
            sk_value: Optional sort key value for the GSI
            limit: Maximum number of items to return
            pk_attr_name: Optional custom partition key attribute name (defaults to {index_name}PK)
            sk_attr_name: Optional custom sort key attribute name (defaults to {index_name}SK)
            
        Returns:
            list: List of items
        """
        try:
            # Use custom attribute names if provided, otherwise use convention
            pk_attr = pk_attr_name or f'{index_name}PK'
            sk_attr = sk_attr_name or f'{index_name}SK'
            
            kwargs = {
                'IndexName': index_name,
                'KeyConditionExpression': Key(pk_attr).eq(pk_value)
            }
            
            if sk_value:
                kwargs['KeyConditionExpression'] &= Key(sk_attr).eq(sk_value)
            
            if limit:
                kwargs['Limit'] = limit
            
            response = self.table.query(**kwargs)
            items = response.get('Items', [])
            
            logger.info(f"Queried {len(items)} items from {index_name}")
            return items
        except ClientError as e:
            logger.error(f"Error querying GSI {index_name}: {e}")
            raise
    
    def check_license_number_exists(self, license_number):
        """
        Check if a license number already exists in the competition
        Uses GSI3 for efficient lookup
        
        Args:
            license_number: License number to check
            
        Returns:
            bool: True if license number exists, False otherwise
        """
        try:
            items = self.query_gsi(
                index_name='GSI3',
                pk_value=license_number,
                pk_attr_name='license_number',
                sk_attr_name='SK',
                limit=1
            )
            exists = len(items) > 0
            if exists:
                logger.info(f"License number {license_number} already exists")
            return exists
        except ClientError as e:
            logger.error(f"Error checking license number {license_number}: {e}")
            raise
    
    def scan_table(self, filter_expression=None, limit=None):
        """
        Scan the entire table (use sparingly)
        
        Args:
            filter_expression: Optional filter expression
            limit: Maximum number of items to return
            
        Returns:
            list: List of items
        """
        try:
            kwargs = {}
            if filter_expression:
                kwargs['FilterExpression'] = filter_expression
            if limit:
                kwargs['Limit'] = limit
            
            response = self.table.scan(**kwargs)
            items = response.get('Items', [])
            
            # Handle pagination
            while 'LastEvaluatedKey' in response and (not limit or len(items) < limit):
                kwargs['ExclusiveStartKey'] = response['LastEvaluatedKey']
                response = self.table.scan(**kwargs)
                items.extend(response.get('Items', []))
            
            logger.info(f"Scanned {len(items)} items from table")
            return items
        except ClientError as e:
            logger.error(f"Error scanning table: {e}")
            raise
    
    def batch_get_items(self, keys):
        """
        Get multiple items in a single request
        
        Args:
            keys: List of (pk, sk) tuples
            
        Returns:
            list: List of items
        """
        try:
            request_items = {
                self.table_name: {
                    'Keys': [{'PK': pk, 'SK': sk} for pk, sk in keys]
                }
            }
            
            response = self.dynamodb.batch_get_item(RequestItems=request_items)
            items = response.get('Responses', {}).get(self.table_name, [])
            
            logger.info(f"Batch got {len(items)} items")
            return items
        except ClientError as e:
            logger.error(f"Error batch getting items: {e}")
            raise
    
    def batch_write_items(self, items_to_put=None, items_to_delete=None):
        """
        Write multiple items in a single request
        
        Args:
            items_to_put: List of items to put
            items_to_delete: List of (pk, sk) tuples to delete
            
        Returns:
            dict: Response from DynamoDB
        """
        try:
            request_items = []
            
            if items_to_put:
                for item in items_to_put:
                    request_items.append({'PutRequest': {'Item': item}})
            
            if items_to_delete:
                for pk, sk in items_to_delete:
                    request_items.append({'DeleteRequest': {'Key': {'PK': pk, 'SK': sk}}})
            
            response = self.dynamodb.batch_write_item(
                RequestItems={self.table_name: request_items}
            )
            
            logger.info(f"Batch wrote {len(request_items)} items")
            return response
        except ClientError as e:
            logger.error(f"Error batch writing items: {e}")
            raise


# Global database client instance
_db_client = None


def get_db_client():
    """
    Get global database client instance
    
    Returns:
        DatabaseClient: Global database client
    """
    global _db_client
    if _db_client is None:
        _db_client = DatabaseClient()
    return _db_client


# Helper functions for common patterns
def generate_id(prefix):
    """
    Generate a unique ID with prefix
    
    Args:
        prefix: Prefix for the ID (e.g., 'crew', 'boat', 'payment')
        
    Returns:
        str: Unique ID
    """
    import uuid
    return f"{prefix}-{uuid.uuid4().hex[:12]}"


def get_timestamp():
    """
    Get current timestamp in ISO format
    
    Returns:
        str: Current timestamp
    """
    return datetime.utcnow().isoformat() + 'Z'


def decimal_to_float(obj):
    """
    Convert Decimal objects to float for JSON serialization
    
    Args:
        obj: Object to convert
        
    Returns:
        Converted object
    """
    if isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, dict):
        return {k: decimal_to_float(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [decimal_to_float(item) for item in obj]
    return obj


def float_to_decimal(obj):
    """
    Convert float objects to Decimal for DynamoDB
    
    Args:
        obj: Object to convert
        
    Returns:
        Converted object
    """
    if isinstance(obj, float):
        return Decimal(str(obj))
    elif isinstance(obj, dict):
        return {k: float_to_decimal(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [float_to_decimal(item) for item in obj]
    return obj
