#!/usr/bin/env python3
"""
PDF Downloader and S3 Uploader

This script:
1. Combines URL links from two files
2. Removes duplicate URLs
3. Downloads PDFs from each URL
4. Uploads PDFs to an S3 bucket
"""

import os
import sys
import time
import logging
import argparse
import requests
import boto3
from urllib.parse import urlparse
from botocore.exceptions import ClientError
from concurrent.futures import ThreadPoolExecutor, as_completed

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("pdf_downloader.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('pdf_downloader')

def setup_argparse():
    """Set up command line arguments"""
    parser = argparse.ArgumentParser(description='Download PDFs and upload to S3')
    parser.add_argument('--input1', default='/Users/bwangyu/Downloads/swire-property-q-business/pdf_links/pdf_links_1.txt',
                        help='First input file with PDF URLs')
    parser.add_argument('--input2', default='/Users/bwangyu/Downloads/swire-property-q-business/pdf_links/pdf_links_2.txt',
                        help='Second input file with PDF URLs')
    parser.add_argument('--output', default='/Users/bwangyu/Downloads/swire-property-q-business/pdf_links/combined_links.txt',
                        help='Output file for combined unique URLs')
    parser.add_argument('--bucket', default='building-dept-pdf-771454898274',
                        help='S3 bucket name')
    parser.add_argument('--temp-dir', default='/Users/bwangyu/Downloads/swire-property-q-business/temp_pdfs',
                        help='Temporary directory for downloaded PDFs')
    parser.add_argument('--max-workers', type=int, default=5,
                        help='Maximum number of concurrent downloads/uploads')
    parser.add_argument('--delay', type=float, default=0.5,
                        help='Delay between downloads (seconds)')
    parser.add_argument('--skip-download', action='store_true',
                        help='Skip downloading PDFs (use existing files)')
    parser.add_argument('--skip-upload', action='store_true',
                        help='Skip uploading PDFs to S3')
    return parser.parse_args()

def read_urls(file_path):
    """Read URLs from a file"""
    try:
        with open(file_path, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    except Exception as e:
        logger.error(f"Error reading {file_path}: {str(e)}")
        return []

def combine_urls(urls1, urls2):
    """Combine URLs and remove duplicates"""
    combined = list(set(urls1 + urls2))
    logger.info(f"Combined {len(urls1)} and {len(urls2)} URLs, resulting in {len(combined)} unique URLs")
    return combined

def save_urls(urls, output_file):
    """Save URLs to a file"""
    try:
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w') as f:
            for url in sorted(urls):
                f.write(f"{url}\n")
        logger.info(f"Saved {len(urls)} URLs to {output_file}")
    except Exception as e:
        logger.error(f"Error saving URLs to {output_file}: {str(e)}")

def get_filename_from_url(url):
    """Extract filename from URL"""
    parsed_url = urlparse(url)
    path = parsed_url.path
    filename = os.path.basename(path)
    
    # If filename doesn't end with .pdf, add it
    if not filename.lower().endswith('.pdf'):
        filename += '.pdf'
    
    return filename

def download_pdf(url, temp_dir):
    """Download a PDF from a URL"""
    filename = get_filename_from_url(url)
    filepath = os.path.join(temp_dir, filename)
    
    # Create directory if it doesn't exist
    os.makedirs(temp_dir, exist_ok=True)
    
    # If file already exists, skip download
    if os.path.exists(filepath):
        logger.debug(f"File already exists: {filepath}")
        return filepath, True
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            with open(filepath, 'wb') as f:
                f.write(response.content)
            logger.info(f"Downloaded: {url} -> {filepath}")
            return filepath, True
        else:
            logger.error(f"Failed to download {url}: Status code {response.status_code}")
            return filepath, False
    except Exception as e:
        logger.error(f"Error downloading {url}: {str(e)}")
        return filepath, False

def upload_to_s3(filepath, bucket, s3_key=None):
    """Upload a file to S3"""
    if s3_key is None:
        s3_key = os.path.basename(filepath)
    
    s3_client = boto3.client('s3')
    try:
        s3_client.upload_file(filepath, bucket, s3_key)
        logger.info(f"Uploaded {filepath} to s3://{bucket}/{s3_key}")
        return True
    except ClientError as e:
        logger.error(f"Error uploading {filepath} to S3: {str(e)}")
        return False

def process_url(url, temp_dir, bucket, skip_download, skip_upload):
    """Process a single URL: download and upload"""
    if skip_download:
        filepath = os.path.join(temp_dir, get_filename_from_url(url))
        download_success = os.path.exists(filepath)
    else:
        filepath, download_success = download_pdf(url, temp_dir)
    
    if download_success and not skip_upload:
        s3_key = get_filename_from_url(url)
        upload_success = upload_to_s3(filepath, bucket, s3_key)
        return url, download_success, upload_success
    
    return url, download_success, False

def main():
    """Main function"""
    args = setup_argparse()
    
    # Read URLs from files
    urls1 = read_urls(args.input1)
    urls2 = read_urls(args.input2)
    
    # Combine URLs and remove duplicates
    combined_urls = combine_urls(urls1, urls2)
    
    # Save combined URLs
    save_urls(combined_urls, args.output)
    
    # Create temp directory if it doesn't exist
    os.makedirs(args.temp_dir, exist_ok=True)
    
    # Process URLs
    success_count = 0
    failure_count = 0
    
    with ThreadPoolExecutor(max_workers=args.max_workers) as executor:
        futures = []
        for url in combined_urls:
            # Add delay between submissions to avoid overwhelming the server
            time.sleep(args.delay)
            future = executor.submit(
                process_url, 
                url, 
                args.temp_dir, 
                args.bucket, 
                args.skip_download, 
                args.skip_upload
            )
            futures.append(future)
        
        for future in as_completed(futures):
            try:
                url, download_success, upload_success = future.result()
                if download_success and upload_success:
                    success_count += 1
                else:
                    failure_count += 1
            except Exception as e:
                logger.error(f"Error processing URL: {str(e)}")
                failure_count += 1
    
    logger.info(f"Processing complete. Successes: {success_count}, Failures: {failure_count}")

if __name__ == "__main__":
    main()
