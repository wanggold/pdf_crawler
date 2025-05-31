#!/usr/bin/env python3
"""
Script to create metadata JSON files for PDF objects in an S3 bucket and upload them back to S3.

For each PDF object in the bucket (e.g., 's3://building-dept-pdf-771454898274/90806-STPA-1000.pdf'),
this script creates a metadata file (e.g., '90806-STPA-1000.pdf.metadata.json') with the following content:
{
    "Attributes":{
        "_source_uri": "https://d30w66uabaix6n.cloudfront.net/90806-STPA-1000.pdf"
    }
}

The metadata file is then uploaded to the same S3 bucket with the path:
's3://building-dept-pdf-771454898274/90806-STPA-1000.pdf.metadata.json'
"""

import boto3
import json
import os
import argparse
from concurrent.futures import ThreadPoolExecutor
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='metadata_creator.log',
    filemode='w'
)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

# Constants
CLOUDFRONT_DOMAIN = "https://d30w66uabaix6n.cloudfront.net/"
TEMP_DIR = "temp_metadata"

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Create metadata files for S3 objects and upload them back to S3.')
    parser.add_argument('--bucket', type=str, default="building-dept-pdf-771454898274",
                        help='S3 bucket name (default: building-dept-pdf-771454898274)')
    parser.add_argument('--max-workers', type=int, default=10,
                        help='Maximum number of worker threads (default: 10)')
    parser.add_argument('--file-extension', type=str, default=".pdf",
                        help='File extension to filter objects (default: .pdf)')
    return parser.parse_args()

def ensure_temp_dir(directory):
    """Ensure the temporary directory exists."""
    if not os.path.exists(directory):
        os.makedirs(directory)
        logging.info(f"Created temporary directory: {directory}")

def create_metadata_file(s3_object_key, temp_dir):
    """Create a metadata JSON file for the given S3 object key."""
    # Extract the filename from the S3 object key
    filename = os.path.basename(s3_object_key)
    
    # Create metadata content
    metadata_content = {
        "Attributes": {
            "_source_uri": f"{CLOUDFRONT_DOMAIN}{filename}"
        }
    }
    
    # Create metadata filename
    metadata_filename = f"{filename}.metadata.json"
    metadata_filepath = os.path.join(temp_dir, metadata_filename)
    
    # Write metadata to file
    with open(metadata_filepath, 'w') as f:
        json.dump(metadata_content, f, indent=4)
    
    logging.info(f"Created metadata file: {metadata_filepath}")
    
    return {
        'local_path': metadata_filepath,
        's3_key': f"{s3_object_key}.metadata.json",
        'metadata_filename': metadata_filename
    }

def upload_metadata_file(s3_client, bucket, metadata_info):
    """Upload the metadata file to S3."""
    try:
        s3_client.upload_file(
            metadata_info['local_path'],
            bucket,
            metadata_info['s3_key']
        )
        logging.info(f"Uploaded {metadata_info['metadata_filename']} to s3://{bucket}/{metadata_info['s3_key']}")
        return True
    except Exception as e:
        logging.error(f"Error uploading {metadata_info['metadata_filename']}: {str(e)}")
        return False

def process_s3_object(s3_client, bucket, s3_object_key, temp_dir):
    """Process a single S3 object: create metadata file and upload it."""
    try:
        metadata_info = create_metadata_file(s3_object_key, temp_dir)
        upload_metadata_file(s3_client, bucket, metadata_info)
    except Exception as e:
        logging.error(f"Error processing {s3_object_key}: {str(e)}")

def main():
    """Main function to process all PDF objects in the S3 bucket."""
    args = parse_arguments()
    
    # Initialize S3 client
    s3_client = boto3.client('s3')
    
    # Ensure temporary directory exists
    ensure_temp_dir(TEMP_DIR)
    
    # List all objects in the bucket
    logging.info(f"Listing objects in bucket: {args.bucket}")
    
    paginator = s3_client.get_paginator('list_objects_v2')
    page_iterator = paginator.paginate(Bucket=args.bucket)
    
    # Collect all PDF objects
    pdf_objects = []
    for page in page_iterator:
        if 'Contents' in page:
            for obj in page['Contents']:
                key = obj['Key']
                # Only process PDF files and skip metadata files
                if key.endswith(args.file_extension) and not key.endswith('.metadata.json'):
                    pdf_objects.append(key)
    
    total_objects = len(pdf_objects)
    logging.info(f"Found {total_objects} {args.file_extension} objects to process")
    
    # Process objects using thread pool
    with ThreadPoolExecutor(max_workers=args.max_workers) as executor:
        for obj_key in pdf_objects:
            executor.submit(process_s3_object, s3_client, args.bucket, obj_key, TEMP_DIR)
    
    logging.info("Processing complete!")

if __name__ == "__main__":
    main()
