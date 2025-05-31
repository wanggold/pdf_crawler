import requests
from bs4 import BeautifulSoup
import urllib.parse
import os
import time
import re
import logging
import argparse
from urllib.robotparser import RobotFileParser

def setup_logger(log_file='pdf_crawler.log', log_level=logging.INFO):
    """Set up and configure logger"""
    # Create logger
    logger = logging.getLogger('pdf_crawler')
    logger.setLevel(log_level)
    
    # Clear any existing handlers
    if logger.handlers:
        logger.handlers = []
    
    # Create file handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(log_level)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    
    # Create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

class PDFCrawler:
    def __init__(self, start_url, output_dir="pdf_links", max_depth=5, log_level=logging.INFO, 
                 url_prefix='https://www.bd.gov.hk/doc/en/resources/codes-and-references/'):
        # Set up logger
        self.logger = setup_logger(log_level=log_level)
        
        self.start_url = start_url
        self.output_dir = output_dir
        self.max_depth = max_depth
        self.url_prefix = url_prefix
        self.visited_urls = set()
        self.pdf_links = set()
        self.domain = urllib.parse.urlparse(start_url).netloc
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
        }
        self.robots_parser = RobotFileParser()
        self.robots_parser.set_url(urllib.parse.urljoin(start_url, '/robots.txt'))
        try:
            self.robots_parser.read()
            self.logger.info(f"Successfully read robots.txt for {self.domain}")
        except Exception as e:
            self.logger.warning(f"Could not read robots.txt: {str(e)}")
    
    def is_allowed(self, url):
        """Check if crawling the URL is allowed by robots.txt"""
        allowed = self.robots_parser.can_fetch(self.headers['User-Agent'], url)
        if not allowed:
            self.logger.warning(f"URL not allowed by robots.txt: {url}")
        return allowed
    
    def normalize_url(self, url, base_url):
        """Normalize URL to absolute form"""
        return urllib.parse.urljoin(base_url, url)
    
    def is_same_domain(self, url):
        """Check if URL belongs to the same domain"""
        parsed_url = urllib.parse.urlparse(url)
        return parsed_url.netloc == self.domain or not parsed_url.netloc
    
    def is_pdf_link(self, url):
        """Check if URL points to a PDF file"""
        return url.lower().endswith('.pdf')
    
    def matches_url_prefix(self, url):
        """Check if URL matches the specified prefix"""
        return url.startswith(self.url_prefix)
    
    def crawl(self, url, depth=0):
        """Crawl the website for PDF links"""
        if depth > self.max_depth:
            self.logger.debug(f"Max depth reached for URL: {url}")
            return
        if url in self.visited_urls:
            self.logger.debug(f"Already visited URL: {url}")
            return
        if not self.is_allowed(url):
            self.logger.info(f"Skipping URL not allowed by robots.txt: {url}")
            return
        
        self.visited_urls.add(url)
        self.logger.info(f"Crawling: {url} (Depth: {depth})")
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code != 200:
                self.logger.warning(f"Failed to fetch {url}: Status code {response.status_code}")
                return
                
            # If it's a PDF, add to our collection if it matches the prefix
            if 'application/pdf' in response.headers.get('Content-Type', ''):
                if not self.url_prefix or self.matches_url_prefix(url):
                    self.pdf_links.add(url)
                    self.logger.info(f"Found PDF: {url}")
                    # Output and save crawled URLs if we have at least 5 links
                    if len(self.pdf_links) >= 5 and len(self.pdf_links) % 5 == 0:
                        self.logger.info(f"Found {len(self.pdf_links)} PDF links so far:")
                        for i, link in enumerate(sorted(self.pdf_links)[-5:], 1):
                            self.logger.info(f"  {i}. {link}")
                        # Save the links found so far
                        self.save_intermediate_results()
                else:
                    self.logger.debug(f"Skipping PDF that doesn't match prefix: {url}")
                return
            
            # Parse HTML content
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all links
            for link in soup.find_all('a', href=True):
                href = link['href']
                absolute_url = self.normalize_url(href, url)
                
                # Check if it's a PDF link
                if self.is_pdf_link(absolute_url):
                    # Only add PDFs that match our prefix (if specified)
                    if not self.url_prefix or self.matches_url_prefix(absolute_url):
                        self.pdf_links.add(absolute_url)
                        self.logger.info(f"Found PDF: {absolute_url}")
                        # Output and save crawled URLs if we have at least 5 links
                        if len(self.pdf_links) >= 5 and len(self.pdf_links) % 5 == 0:
                            self.logger.info(f"Found {len(self.pdf_links)} PDF links so far:")
                            for i, link in enumerate(sorted(self.pdf_links)[-5:], 1):
                                self.logger.info(f"  {i}. {link}")
                            # Save the links found so far
                            self.save_intermediate_results()
                    else:
                        self.logger.debug(f"Skipping PDF that doesn't match prefix: {absolute_url}")
                # Otherwise, if it's the same domain, crawl it
                elif self.is_same_domain(absolute_url) and absolute_url not in self.visited_urls:
                    # Add a small delay to be respectful
                    time.sleep(1)
                    self.crawl(absolute_url, depth + 1)
                    
        except Exception as e:
            self.logger.error(f"Error crawling {url}: {str(e)}", exc_info=True)
    
    def save_intermediate_results(self):
        """Save the found PDF links to a file during crawling"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            self.logger.info(f"Created output directory: {self.output_dir}")
        
        output_file = os.path.join(self.output_dir, 'pdf_links.txt')
        with open(output_file, 'w') as f:
            for link in sorted(self.pdf_links):
                f.write(f"{link}\n")
        
        self.logger.info(f"Intermediate results saved to {output_file}")
    
    def save_results(self):
        """Save the found PDF links to a file at the end of execution"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            self.logger.info(f"Created output directory: {self.output_dir}")
        
        output_file = os.path.join(self.output_dir, 'pdf_links.txt')
        with open(output_file, 'w') as f:
            for link in sorted(self.pdf_links):
                f.write(f"{link}\n")
        
        # Calculate residual links (those not displayed in complete batches of 5)
        total_links = len(self.pdf_links)
        residual_count = total_links % 5
        
        # If there are residual links that weren't displayed in batches of 5
        if residual_count > 0:
            self.logger.info(f"Remaining {residual_count} PDF links found:")
            for i, link in enumerate(sorted(self.pdf_links)[-residual_count:], 1):
                self.logger.info(f"  {i}. {link}")
        
        self.logger.info(f"Crawl completed. Found {total_links} PDF links.")
        self.logger.info(f"Final results saved to {output_file}")

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Crawl a website for PDF links')
    parser.add_argument('--start-url', default="https://www.bd.gov.hk/en/resources/codes-and-references/",
                        help='Starting URL to crawl')
    parser.add_argument('--output-dir', default="pdf_links",
                        help='Directory to save PDF links')
    parser.add_argument('--max-depth', type=int, default=5,
                        help='Maximum crawl depth')
    parser.add_argument('--url-prefix', 
                        default='https://www.bd.gov.hk/doc/en/resources/codes-and-references/',
                        help='Only include PDFs with this URL prefix')
    parser.add_argument('--debug', action='store_true',
                        help='Enable debug logging')
    
    args = parser.parse_args()
    
    # Configure logging level
    log_level = logging.DEBUG if args.debug else logging.INFO
    
    # Create and run crawler
    crawler = PDFCrawler(
        start_url=args.start_url,
        output_dir=args.output_dir,
        max_depth=args.max_depth,
        log_level=log_level,
        url_prefix=args.url_prefix
    )
    crawler.crawl(args.start_url)
    crawler.save_results()
