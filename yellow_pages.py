import requests
from lxml import html
import unicodecsv as csv
import argparse
import math
import urllib3

# Remove https error
urllib3.disable_warnings()

scraped_results = []
base_url = "https://www.yellowpages.com"
headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
           'Accept-Encoding': 'gzip, deflate, br',
           'Accept-Language': 'en-GB,en;q=0.9,en-US;q=0.8,ml;q=0.7',
           'Cache-Control': 'max-age=0',
           'Connection': 'keep-alive',
           'Host': 'www.yellowpages.com',
           'Upgrade-Insecure-Requests': '1',
           'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36'
           }

def list_id(url):
    # Adding retries
    for retry in range(10):
        try:
            response = requests.get(url, verify=False, headers=headers)
            print("parsing: " + url)
            if response.status_code == 200:
                parser = html.fromstring(response.text)
                parser.make_links_absolute(base_url)

                XPATH_LISTINGS = "//main[@id='bpp']"
                listings = parser.xpath(XPATH_LISTINGS)

                business_details = {}

                for results in listings:
                    XPATH_EMAIL = ".//header[@id='main-header']//div[@class='business-card-footer']//a[@class='email-business']//@href"
                    XPATH_YIB = ".//header[@id='main-header']//article[contains(@class,'business-card')]//section[@class='primary-info']//div[@class='years-in-business']//div[@class='count']//div[@class='number']//text()"
                    XPATH_GI = ".//article[@id='main-article']//section[@id='main-section']//section[@id='business-info']//dl//dd[@class='general-info']//text()"
                    XPATH_CATEGORY = ".//article[@id='main-article']//section[@id='main-section']//section[@id='business-info']//dl//dd[@class='categories']//text()"
                    XPATH_NB = ".//article[@id='main-article']//section[@id='main-section']//section[@id='business-info']//dl//dd[@class='neighborhoods']//text()"
                    XPATH_SERVICES = ".//article[@id='main-article']//section[@id='main-section']//section[@id='business-info']//dl//dd[@class='features-services']//text()"

                    raw_email = results.xpath(XPATH_EMAIL)
                    raw_yib = results.xpath(XPATH_YIB)
                    raw_gi = results.xpath(XPATH_GI)
                    raw_category = results.xpath(XPATH_CATEGORY)
                    raw_nb = results.xpath(XPATH_NB)
                    raw_services = results.xpath(XPATH_SERVICES)

                    business_email = ''.join(raw_email).strip() if raw_email else 'mailto:'
                    business_yib = ''.join(raw_yib).strip() if raw_yib else None
                    business_gi = ''.join(raw_gi).strip() if raw_gi else None
                    business_category = ''.join(raw_category).strip() if raw_category else None
                    business_nb = ''.join(raw_nb).strip() if raw_nb else None
                    business_services = ''.join(raw_services).strip() if raw_services else None

                    business_details = {
                        'email': business_email.split("mailto:")[1],
                        'yib': business_yib,
                        'gi': business_gi,
                        'category': business_category,
                        'neighborhoods': business_nb,
                        'services': business_services,
                    }

                return business_details

            elif response.status_code == 404:
                print("Could not find a location matching", place)
                # no need to retry for non existing page
                break
            else:
                print("Failed to process page")
                return []

        except:
            print("Failed to process page")
            return []

def parse_listing(keyword, place, page):
    url = base_url + "/search?search_terms={0}&geo_location_terms={1}&page={2}".format(keyword, place, page)

    # Adding retries
    for retry in range(10):
        try:
            response = requests.get(url, verify=False, headers=headers)
            print("parsing: " + url)
            if response.status_code == 200:
                parser = html.fromstring(response.text)
                parser.make_links_absolute(base_url)

                XPATH_LISTINGS = "//div[@class='search-results organic']//div[@class='v-card']"
                listings = parser.xpath(XPATH_LISTINGS)

                for results in listings:
                    XPATH_ID = ".//a[@class='business-name']//@href"
                    XPATH_BUSINESS_NAME = ".//a[@class='business-name']//text()"
                    XPATH_BUSSINESS_PAGE = ".//a[@class='business-name']//@href"
                    XPATH_phone = ".//div[@class='info']//div[contains(@class,'info-section')]//*[@class='phones phone primary']//text()"
                    XPATH_ADDRESS = ".//div[@class='info']//div[@class='info-section info-primary']//p[@class='adr']//text()"
                    XPATH_WEBSITE = ".//div[@class='info']//div[contains(@class,'info-section')]//div[@class='links']//a[contains(@class,'track-visit-website')]/@href"
                    XPATH_RATING = ".//div[@class='info']//div[contains(@class,'info-section')]//div[contains(@class,'result-rating')]//span//text()"

                    raw_business_id = results.xpath(XPATH_ID)
                    raw_business_name = results.xpath(XPATH_BUSINESS_NAME)
                    raw_business_phone = results.xpath(XPATH_phone)
                    raw_business_page = results.xpath(XPATH_BUSSINESS_PAGE)
                    raw_website = results.xpath(XPATH_WEBSITE)
                    raw_rating = results.xpath(XPATH_RATING)
                    address = results.xpath(XPATH_ADDRESS)

                    business_id = ''.join(raw_business_id).strip() if raw_business_id else None
                    business_name = ''.join(raw_business_name).strip() if raw_business_name else None
                    phone = ''.join(raw_business_phone).strip() if raw_business_phone else None
                    business_page = ''.join(raw_business_page).strip() if raw_business_page else None
                    website = ''.join(raw_website).strip() if raw_website else None
                    rating = ''.join(raw_rating).replace("(", "").replace(")", "").strip() if raw_rating else None
                    address = ''.join(address).strip() if address else None

                    business_details = {
                        'id': business_id.split("?lid=")[1],
                        'business_name': business_name,
                        'phone': phone,
                        'email': list_id(business_page)['email'],
                        'years_in_business': list_id(business_page)['yib'],
                        'general_info': list_id(business_page)['gi'],
                        'business_page': business_page,
                        'category': list_id(business_page)['category'],
                        'neighborhoods': list_id(business_page)['neighborhoods'],
                        'services': list_id(business_page)['services'],
                        'website': website,
                        'rating': rating,
                        'address': address,
                        'keyword': keyword,
                        'place': place,
                    }
                    scraped_results.append(business_details)

                return scraped_results

            elif response.status_code == 404:
                print("Could not find a location matching", place)
                # no need to retry for non existing page
                break
            else:
                print("Failed to process page")
                return []

        except:
            print("Failed to process page")
            return []


if __name__ == "__main__":

    argparser = argparse.ArgumentParser()
    argparser.add_argument('keyword', help='Search Keyword')
    argparser.add_argument('place', help='Place Name')
    argparser.add_argument('count', help='Page Counts')
    args = argparser.parse_args()
    keyword = args.keyword
    place = args.place
    count = int(args.count)
    cardPerPage = 30

    for page in range(math.ceil(count / cardPerPage)):
        parse_listing(keyword, place, page + 1)

    if scraped_results:
        print("Writing scraped data to data.csv")
        with open('data.csv', 'wb') as csvfile:
            fieldnames = ['id', 'business_name', 'phone', 'email', 'years_in_business', 'services', 'neighborhoods', 'general_info', 'business_page', 'category', 'website', 'address',
                          'rating', 'keyword', 'place']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
            writer.writeheader()
            for data in scraped_results:
                writer.writerow(data)
