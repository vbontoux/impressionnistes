#!/usr/bin/env python3
"""
Reinitialize database configuration by invoking InitConfig Lambda
Used by db-reset Makefile target
"""
import json
import sys
import boto3

def main():
    if len(sys.argv) != 2:
        print("Usage: reinit_config.py <region>")
        sys.exit(1)
    
    region = sys.argv[1]
    
    # Find InitConfig function
    lambda_client = boto3.client('lambda', region_name=region)
    
    try:
        response = lambda_client.list_functions()
        init_functions = [
            f['FunctionName'] for f in response['Functions']
            if 'InitConfigFunction' in f['FunctionName'] and 'Provider' not in f['FunctionName']
        ]
        
        if not init_functions:
            print("⚠️  Warning: InitConfig function not found - skipping")
            return
        
        function_name = init_functions[0]
        
        # Invoke the function
        payload = {
            "RequestType": "Update",
            "ResourceProperties": {}
        }
        
        response = lambda_client.invoke(
            FunctionName=function_name,
            InvocationType='RequestResponse',
            Payload=json.dumps(payload)
        )
        
        # Check response
        if response['StatusCode'] == 200:
            print("✓ Configuration reinitialized")
        else:
            print(f"⚠️  Init function returned status {response['StatusCode']}")
            
    except Exception as e:
        print(f"⚠️  Warning: Failed to reinitialize config: {e}")
        print("   You can manually reinitialize by running: make deploy-dev")

if __name__ == '__main__':
    main()
