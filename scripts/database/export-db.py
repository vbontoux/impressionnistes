#!/usr/bin/env python3
"""
Export DynamoDB table to CSV
"""
import json
import csv
import sys
import argparse
from datetime import datetime
from pathlib import Path


def flatten_dynamodb_item(item):
    """Flatten DynamoDB item structure to simple key-value pairs"""
    flattened = {}
    for key, value in item.items():
        if isinstance(value, dict):
            # Handle DynamoDB type descriptors (S, N, BOOL, etc.)
            if len(value) == 1:
                type_key = list(value.keys())[0]
                flattened[key] = value[type_key]
            else:
                # Nested object - convert to JSON string
                flattened[key] = json.dumps(value)
        elif isinstance(value, list):
            flattened[key] = json.dumps(value)
        else:
            flattened[key] = value
    return flattened


def export_to_csv(json_file, output_file=None):
    """Convert DynamoDB JSON export to CSV"""
    # Read JSON file
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    items = data.get('Items', [])
    
    if not items:
        print("No items found in export")
        return
    
    # Flatten all items
    flattened_items = [flatten_dynamodb_item(item) for item in items]
    
    # Get all unique keys
    all_keys = set()
    for item in flattened_items:
        all_keys.update(item.keys())
    
    # Sort keys for consistent output
    fieldnames = sorted(all_keys)
    
    # Determine output file
    if not output_file:
        json_path = Path(json_file)
        output_file = json_path.parent / f"{json_path.stem}.csv"
    
    # Write CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(flattened_items)
    
    print(f"✓ CSV exported to: {output_file}")
    print(f"  Items: {len(flattened_items)}")
    print(f"  Columns: {len(fieldnames)}")


def export_by_entity(json_file, output_dir):
    """Export different entity types to separate CSV files"""
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    items = data.get('Items', [])
    
    # Group by PK prefix
    entities = {}
    for item in items:
        pk = item.get('PK', {}).get('S', 'UNKNOWN')
        entity_type = pk.split('#')[0] if '#' in pk else pk
        
        if entity_type not in entities:
            entities[entity_type] = []
        entities[entity_type].append(flatten_dynamodb_item(item))
    
    # Export each entity type
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    
    for entity_type, entity_items in entities.items():
        if not entity_items:
            continue
        
        # Get all keys for this entity type
        all_keys = set()
        for item in entity_items:
            all_keys.update(item.keys())
        
        fieldnames = sorted(all_keys)
        
        output_file = output_path / f"{entity_type.lower()}-{timestamp}.csv"
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(entity_items)
        
        print(f"✓ {entity_type}: {len(entity_items)} items → {output_file}")


def main():
    parser = argparse.ArgumentParser(description='Export DynamoDB table to CSV')
    parser.add_argument('json_file', help='Input JSON file from DynamoDB scan')
    parser.add_argument('-o', '--output', help='Output CSV file')
    parser.add_argument('-s', '--split', action='store_true', 
                       help='Split by entity type into separate files')
    parser.add_argument('-d', '--output-dir', default='exports',
                       help='Output directory for split files (default: exports)')
    
    args = parser.parse_args()
    
    if args.split:
        export_by_entity(args.json_file, args.output_dir)
    else:
        export_to_csv(args.json_file, args.output)


if __name__ == '__main__':
    main()
