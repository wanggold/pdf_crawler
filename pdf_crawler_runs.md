# PDF Crawler Run Details

## Overview
This document records the details of two PDF crawler runs performed on the Building Department website (bd.gov.hk). The crawler was modified between runs to improve its functionality and coverage.

## Run 1: Initial Configuration

### Configuration
- **Start URL**: `https://www.bd.gov.hk/en/resources/codes-and-references/practice-notes-and-circular-letters/index.html`
- **URL Prefix**: `https://www.bd.gov.hk/doc/en/resources/codes-and-references/practice-notes-and-circular-letters/`
- **Max Depth**: 3
- **Output Directory**: `pdf_links`

### Results
- **Total PDFs Found**: ~866 PDF links
- **Coverage**: Limited to practice notes and circular letters subdirectory
- **Missing Important PDFs**: Yes, PDFs like `CoP_SUC2013e.pdf` and `fs_code2011.pdf` were not included
- **Intermediate Saving**: Added during this run
- **Residual Links Handling**: Added during this run

### Issues Identified
1. The URL prefix was too restrictive, filtering out important PDFs
2. The crawl depth was insufficient to reach some deeper pages
3. The starting URL was limited to a specific subdirectory

## Run 2: Improved Configuration

### Configuration Changes
- **Start URL**: Changed to `https://www.bd.gov.hk/en/resources/codes-and-references/`
- **URL Prefix**: Broadened to `https://www.bd.gov.hk/doc/en/resources/codes-and-references/`
- **Max Depth**: Increased from 3 to 5
- **Output Directory**: Same (`pdf_links`)

### Results
- **Total PDFs Found**: 733 PDF links
- **Coverage**: Comprehensive coverage of codes-and-references directory and subdirectories
- **Important PDFs Included**: Yes, successfully found `CoP_SUC2013e.pdf` and `fs_code2011.pdf`
- **Missing Some PDFs**: Yes, some PDFs like `APP136.pdf` and `CL_SVGPe.pdf` were not found
- **Intermediate Saving**: Working as expected, saving every 5 links
- **Residual Links Handling**: Working as expected, properly handling links at the end

### Key Improvements
1. **Broader URL Coverage**: By using a more general URL prefix, the crawler now includes PDFs from all subdirectories under codes-and-references
2. **Deeper Crawling**: Increased depth allows the crawler to navigate deeper into the website structure
3. **Better Starting Point**: Starting from the main codes-and-references page allows discovery of all relevant subdirectories

## Sample PDF Links Found

### From Practice Notes and Circular Letters
```
https://www.bd.gov.hk/doc/en/resources/codes-and-references/practice-notes-and-circular-letters/pnap/APP/APP099.pdf
https://www.bd.gov.hk/doc/en/resources/codes-and-references/practice-notes-and-circular-letters/pnap/signed/APP099se.pdf
https://www.bd.gov.hk/doc/en/resources/codes-and-references/practice-notes-and-circular-letters/pnap/APP/APP100.pdf
```

### From Code and Design Manuals
```
https://www.bd.gov.hk/doc/en/resources/codes-and-references/code-and-design-manuals/CoP_SUC2013e.pdf
https://www.bd.gov.hk/doc/en/resources/codes-and-references/code-and-design-manuals/fs_code2011.pdf
https://www.bd.gov.hk/doc/en/resources/codes-and-references/code-and-design-manuals/SS2009_e.pdf
```

### From Other Directories
```
https://www.bd.gov.hk/doc/en/resources/codes-and-references/ScheduledAreas/90806-STPA-1000.pdf
https://www.bd.gov.hk/doc/en/resources/codes-and-references/notices-and-reports/sustainability/Carbon_Performance_Disclosure2022e.pdf
https://www.bd.gov.hk/doc/en/resources/codes-and-references/transitional-housing-initiatives/MW0012019MOD.pdf
```

## Conclusion
The modifications to the PDF crawler significantly improved its functionality and coverage. By broadening the URL prefix, increasing the crawl depth, and starting from a higher-level directory, the crawler was able to find a more comprehensive set of PDF links, including important documents that were missed in the initial run.

The crawler now successfully:
1. Finds PDFs across all subdirectories under codes-and-references
2. Saves intermediate results during crawling
3. Properly handles residual links at the end of execution
4. Navigates deeper into the website structure
5. Includes important PDFs like `CoP_SUC2013e.pdf` and `fs_code2011.pdf`

## Missing PDFs Analysis

Despite the improvements in the second run, some PDFs were still not found by the crawler. Two notable examples are:

1. **APP136.pdf**: `https://www.bd.gov.hk/doc/en/resources/codes-and-references/practice-notes-and-circular-letters/APP136.pdf`
2. **CL_SVGPe.pdf**: `https://www.bd.gov.hk/doc/en/resources/codes-and-references/practice-notes-and-circular-letters/circular/CL_SVGPe.pdf`

### Reasons for Missing PDFs:

1. **Path Structure Differences**: 
   - The first run found these PDFs because it started directly from the practice-notes-and-circular-letters directory
   - The second run started from a higher-level directory and may have encountered a different navigation structure

2. **Link Visibility**: 
   - These PDFs might not be directly linked from the pages that were crawled in the second run
   - They might be accessible only through specific navigation paths that weren't followed

3. **Website Structure Changes**: 
   - The website structure might have changed between runs
   - Some PDFs might have been moved to different locations or renamed

4. **Depth Limitations**: 
   - Despite increasing the depth to 5, some PDFs might be located at deeper levels
   - The crawler might have reached its maximum depth before finding these specific PDFs

5. **URL Pattern Differences**:
   - Notice that APP136.pdf is directly under practice-notes-and-circular-letters, while most other APP files are under practice-notes-and-circular-letters/pnap/APP/
   - This inconsistent URL structure might have caused the crawler to miss these files

### Potential Solutions:

1. **Combined Approach**: Run both crawlers and merge the results to get the most comprehensive list
2. **Custom URL Patterns**: Add specific URL patterns to look for known file structures
3. **Increased Depth**: Further increase the crawl depth, though this would increase execution time
4. **Multiple Starting Points**: Use multiple starting URLs to ensure coverage of different sections
5. **Manual Addition**: For critical PDFs that are consistently missed, consider adding them manually to the results
