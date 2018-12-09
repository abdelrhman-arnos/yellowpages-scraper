import requests
from lxml import html
import unicodecsv as csv
import argparse


def parse_listing(keyword, place, page):
    """

    Function to process yellowpage listing page
    : param keyword: search query
       : param place : place name

    """
    url = "https://www.yellowpages.com/search?search_terms={0}&geo_location_terms={1}&page={2}".format(keyword, place,
                                                                                                       page)
    print("retrieving ", url)

    headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
               'Accept-Encoding': 'gzip, deflate, br',
               'Accept-Language': 'en-GB,en;q=0.9,en-US;q=0.8,ml;q=0.7',
               'Cache-Control': 'max-age=0',
               'Connection': 'keep-alive',
               'Host': 'www.yellowpages.com',
               'Upgrade-Insecure-Requests': '1',
               'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36'
               }
    # Adding retries
    for retry in range(10):
        try:
            response = requests.get(url, verify=False, headers=headers)
            print("parsing page")
            if response.status_code == 200:
                parser = html.fromstring(response.text)
                # making links absolute
                base_url = "https://www.yellowpages.com"
                parser.make_links_absolute(base_url)


                XPATH_LISTINGS = "//div[@class='search-results organic']//div[@class='v-card']"
                listings = parser.xpath(XPATH_LISTINGS)
                scraped_results = []

                XPATH_PAGINATION = "//div[@class='pagination']//p//text()"
                pagination = parser.xpath(XPATH_PAGINATION)[1]

                for results in listings:
                    XPATH_ID = ".//a[@class='business-name']//@href"
                    XPATH_BUSINESS_NAME = ".//a[@class='business-name']//text()"
                    XPATH_BUSSINESS_PAGE = ".//a[@class='business-name']//@href"
                    XPATH_phone = ".//div[@class='info']//div[contains(@class,'info-section')]//*[@class='phones phone primary']//text()"
                    XPATH_ADDRESS = ".//div[@class='info']//div[contains(@class,'info-section')]//p[@class='adr']//text()"
                    XPATH_CATEGORIES = ".//div[@class='info']//div[contains(@class,'info-section')]//div[@class='categories']//text()"
                    XPATH_WEBSITE = ".//div[@class='info']//div[contains(@class,'info-section')]//div[@class='links']//a[contains(@class,'track-visit-website')]/@href"
                    XPATH_RATING = ".//div[@class='info']//div[contains(@class,'info-section')]//div[contains(@class,'result-rating')]//span//text()"
                    # XPATH_EMAIL = ".//div[@class='info']//div[contains(@class,'info-section')]//div[contains(@class,'result-rating')]//span//text()"

                    raw_business_id = results.xpath(XPATH_ID)
                    raw_business_name = results.xpath(XPATH_BUSINESS_NAME)
                    raw_business_phone = results.xpath(XPATH_phone)
                    raw_business_page = results.xpath(XPATH_BUSSINESS_PAGE)
                    raw_categories = results.xpath(XPATH_CATEGORIES)
                    raw_website = results.xpath(XPATH_WEBSITE)
                    raw_rating = results.xpath(XPATH_RATING)
                    address = results.xpath(XPATH_ADDRESS)

                    business_id = ''.join(raw_business_id).strip() if raw_business_id else None
                    business_name = ''.join(raw_business_name).strip() if raw_business_name else None
                    phone = ''.join(raw_business_phone).strip() if raw_business_phone else None
                    business_page = ''.join(raw_business_page).strip() if raw_business_page else None
                    category = ','.join(raw_categories).strip() if raw_categories else None
                    website = ''.join(raw_website).strip() if raw_website else None
                    rating = ''.join(raw_rating).replace("(", "").replace(")", "").strip() if raw_rating else None
                    address = ''.join(address).strip() if address else None

                    business_details = {
                        'id': business_id.split("?lid=")[1],
                        'business_name': business_name,
                        'phone': phone,
                        'business_page': business_page,
                        'category': category,
                        'website': website,
                        'rating': rating,
                        'address': address,
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
    argparser.add_argument('page', help='Page Name')

    args = argparser.parse_args()
    keyword = args.keyword
    place = args.place
    page = args.page
    scraped_data = parse_listing(keyword, place, page)

    if scraped_data:
        print("Writing scraped data to %s-%s.csv" % (keyword, place))
        with open('%s-%s.csv' % (keyword, place), 'wb') as csvfile:
            fieldnames = ['id', 'business_name', 'phone', 'business_page', 'category', 'website', 'address', 'rating']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
            writer.writeheader()
            for data in scraped_data:
                writer.writerow(data)
