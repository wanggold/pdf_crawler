# Amazon Q Business: Building Department PDF Crawler and Uploader

This project contains scripts to crawl the Building Department website for PDF links, download the PDFs, and upload them to an S3 bucket. The PDFs are used to create knowledge base for Amazon Q Business. 

## Scripts

### 1. PDF Crawler (`pdf_crawler.py`)

Crawls the Building Department website to find PDF links.

**Features:**
- Configurable starting URL and crawl depth
- URL prefix filtering
- Intermediate results saving
- Residual links handling
- Debug mode for detailed logging

**Usage:**
```bash
python3 pdf_crawler.py [--start-url URL] [--output-dir DIR] [--max-depth DEPTH] [--url-prefix PREFIX] [--debug]
```

**Example:**
```bash
# Run with default settings
python3 pdf_crawler.py

# Run with custom settings
python3 pdf_crawler.py --start-url "https://www.bd.gov.hk/en/resources/codes-and-references/" --max-depth 5 --debug
```

### 2. PDF Downloader and S3 Uploader (`pdf_downloader.py`)

Combines PDF links from multiple sources, downloads the PDFs, and uploads them to an S3 bucket.

**Features:**
- Combines URLs from multiple files
- Removes duplicate URLs
- Downloads PDFs with error handling
- Uploads PDFs to S3
- Concurrent processing with configurable workers
- Rate limiting to avoid overwhelming servers

**Usage:**
```bash
python3 pdf_downloader.py [--input1 FILE1] [--input2 FILE2] [--output OUTPUT] [--bucket BUCKET] [--temp-dir DIR] [--max-workers N] [--delay SECONDS] [--skip-download] [--skip-upload]
```

**Example:**
```bash
# Run with default settings
python3 pdf_downloader.py

# Run with custom settings
python3 pdf_downloader.py --max-workers 10 --delay 1.0 --bucket "my-custom-bucket"

# Skip download (use existing files) and only upload
python3 pdf_downloader.py --skip-download

# Skip upload and only download
python3 pdf_downloader.py --skip-upload
```

### 3. Metadata Creator (`create_metadata_files.py`)

Creates metadata JSON files for PDF objects in an S3 bucket and uploads them back to S3. For each PDF in the bucket, it creates a metadata file with a CloudFront URL and uploads it to the same location. This follows the [Amazon Q Business source attribution URL pattern](https://community.aws/content/2jHkgsngSxBhkzFPQwuEMgl3Nkw/setting-up-source-attribution-urls-when-using-amazon-s3-as-a-connector-for-amazon-q-business-applications?lang=en).

**Features:**
- Automatically lists all PDF objects in the specified S3 bucket
- Creates metadata files with CloudFront URLs
- Uploads metadata files to the same S3 bucket
- Multithreaded processing for faster execution
- Configurable CloudFront domain
- Detailed logging

**Usage:**
```bash
python3 create_metadata_files.py [--bucket BUCKET] [--max-workers N] [--file-extension EXT]
```

**Example:**
```bash
# Run with default settings
python3 create_metadata_files.py

# Run with custom settings
python3 create_metadata_files.py --bucket "my-custom-bucket" --max-workers 20

# Process files with a different extension
python3 create_metadata_files.py --file-extension ".docx"
```

## File Structure

- `pdf_crawler.py`: The web crawler script
- `pdf_downloader.py`: The PDF downloader and S3 uploader script
- `create_metadata_files.py`: The metadata creator script
- `pdf_crawler_runs.md`: Documentation of crawler runs and analysis
- `pdf_links/`: Directory containing PDF links
  - `pdf_links_1.txt`: Results from the first crawler run
  - `pdf_links_2.txt`: Results from the second crawler run
  - `combined_links.txt`: Combined unique links from both runs
- `temp_pdfs/`: Temporary directory for downloaded PDFs
- `temp_metadata/`: Temporary directory for metadata files

## Requirements

- Python 3.6+
- Required Python packages:
  - requests
  - beautifulsoup4
  - boto3
  - urllib3

Install requirements:
```bash
pip install requests beautifulsoup4 boto3 urllib3
```

## AWS Configuration

Before running the S3 upload functionality, ensure AWS credentials are properly configured:

1. Install the AWS CLI:
   ```bash
   pip install awscli
   ```

2. Configure AWS credentials:
   ```bash
   aws configure
   ```

3. Enter your AWS Access Key ID, Secret Access Key, default region, and output format when prompted.

Alternatively, you can set environment variables:
```bash
export AWS_ACCESS_KEY_ID="your_access_key"
export AWS_SECRET_ACCESS_KEY="your_secret_key"
export AWS_DEFAULT_REGION="your_region"
```

## Notes

- The crawler respects robots.txt rules
- Rate limiting is implemented to avoid overwhelming the server
- Error handling is in place for both downloading and uploading
- Logs are saved to `pdf_crawler.log` and `pdf_downloader.log`
