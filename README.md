# Yellow Pages Business Details Scraper :rocket:
Scraping Business Details with multi processing concept from https://www.yellowpages.com where the (Keyword, place, Count) using Python and LXML to CSV file.

## Getting Started
These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Fields
Extracting possible fields from the search page and specific business card details in search page:

| Field Name (search) | Field Name (specific) |
| ------------- | ------------- |
| ID | Email  |
| Business name | Years in business  |
| Phone | General info  |
| page(href) | General info  |
| Address | Category  |
| Website | Neighborhoods  |
| Rating | Services  |

### Libraries
This script built using Python 3 and:

- requests -- *For calling Yellow Pages URLs*
- lxml -- *To convert the HTML to string*
- unicodecsv -- *Export the data to CSV file*
- argparse -- *Handling arguments passes to script*
- math -- *Calculate to get page number*
- urllib3 -- *Remove https error*
- multiprocessing -- *To use multi process to finish the script faster*
- time -- *Calculate to getting time spent to finish*

## How to run the script
You Need to run the script name followed by the positional arguments **keyword** and **place** and **count**, the script working well with small/capital cases :+1:
**count** argument is count of business cards in the search page [example](https://www.screencast.com/t/0taqV55C8mB) used to looping on all business cards related the **keyword** and **place**
Here is an example to find the business details for a digital agency in Los Angeles, CA.

```
python yellow_pages.py digital+agency Los+Angeles,+CA 64
```

## Sample Output
This will create a CSV file:
[Sample output](https://raw.githubusercontent.com/abdelrhman-m27/yellowpages-scraper/master/digital+agency-Los+Angeles,+CA.csv)
