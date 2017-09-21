from gevent import monkey

monkey.patch_all()

import os
import time
import signal
import logging
import json
import gevent
import urllib
import re
from flask import Flask, request
from gevent.pywsgi import WSGIServer
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from flask_cors import CORS

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s '
                           '[%(threadName)s] '
                           '[%(levelname)s] '
                           '%(name)s - '
                           '%(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S %z')
logger = logging.getLogger(__name__)

app = Flask(__name__)

CORS(
    app,
    origins=["http://localhost:3000"],
    supports_credentials=True
)

chrome_options = Options()
chrome_options.add_argument("--headless")
# chrome_options.binary_location = '/Applications/Google Chrome Canary.app'

driver = webdriver.Chrome(chrome_options=chrome_options)


@app.route("/")
def health_test():
    logger.info(time.time())
    logger.debug("HEALTH OKAY")
    time.sleep(5)
    return "HEALTH OKAY"


@app.route("/ads/craigslist", methods=["POST"])
def create_ad_collection():
    body = json.loads(request.data)
    search_string = body.get("search_string")
    return json.dumps(craigslist_request(search_string))
    # return get_ad_data(search_string)


# @app.route("/ads/ebay", methods=["POST"])
# def create_ad_collection():
#     body = json.loads(request.data)
#     search_string = body.get("search_string")
#     return json.dumps(craigslist_request(search_string))


def get_ad_data(search_string):
    requests = gevent.joinall(
        [gevent.spawn(craigslist_request, search_string), gevent.spawn(ebay_request, search_string)])

    return [request in requests]


def craigslist_request(search_string):
    driver.get("https://seattle.craigslist.org/search/sss?query={0}".format(urllib.quote_plus(search_string)))
    soup = BeautifulSoup(driver.page_source, "html.parser")
    ul_list = soup.find_all("ul", class_="rows")
    li_list = ul_list[0].find_all("li", class_="result-row")

    items = []

    for li in li_list:
        items.append(
            {"source": "Craigslist", "location": get_location(li), "title": get_title(li), "price": get_price(li),
             "image": get_image(li)})

    return items


def get_title(li):
    try:
        return li.find("a", class_="result-title hdrlnk").get_text()
    except:
        logger.info("title missing from ad {0}".format(li))
        return ""


def get_price(li):
    try:
        return li.find("span", class_="result-price").get_text()
    except:
        logger.info("price missing from ad {0}".format(li))
        return None


def get_image(li):
    try:
        return li.find("a", class_="result-image gallery").img['src']
    except:
        logger.info("title missing from ad {0}".format(li))
        return None


def get_location(li):
    try:
        return re.sub("[()]", "", li.find("span", class_="result-hood").get_text())
    except:
        logger.info("location missing from ad {0}".format(li))
        return None


def ebay_request(search_string):
    pass


def facebook_request(search_string):
    pass


def on_sigint(signal, frame):
    driver.close()
    os._exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, on_sigint)
    server = WSGIServer(('', int(5000)), app)
    server.serve_forever()



# import os
# import uuid
# import logging
# from Item import Item
# from selenium import webdriver
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.chrome.options import Options
# from bs4 import BeautifulSoup
#
# logging.basicConfig(level=logging.INFO,
#                     format='%(asctime)s '
#                            '[%(threadName)s] '
#                            '[%(levelname)s] '
#                            '%(name)s - '
#                            '%(message)s',
#                     datefmt='%Y-%m-%d %H:%M:%S %z')
# logger = logging.getLogger(__name__)
#
# chrome_options = Options()
# chrome_options.add_argument("--headless")
# # chrome_options.binary_location = '/Applications/Google Chrome Canary.app'
#
# driver = webdriver.Chrome(chrome_options=chrome_options)
# driver.get("https://seattle.craigslist.org/search/sss?query=table%20saw&sort=rel")
#
# soup = BeautifulSoup(driver.page_source, "html.parser")
# ul_list = soup.find_all("ul", class_="rows")
# li_list = ul_list[0].find_all("li", class_="result-row")
#
# items = {}
#
#
# def insert_new_item(li):
#     items[uuid.uuid4()] = Item(get_title(li), price=get_price(li), image=get_image(li))
#
#
# def get_title(li):
#     try:
#         return li.find("a", class_="result-title hdrlnk").get_text()
#     except:
#         logger.info("title missing from ad {0}".format(li))
#         return ""
#
#
# def get_price(li):
#     try:
#         return li.find("span", class_="result-price").get_text()
#     except:
#         logger.info("price missing from ad {0}".format(li))
#         return None
#
#
# def get_image(li):
#     try:
#         return li.find("a", class_="result-image gallery").img['src']
#     except:
#         logger.info("title missing from ad {0}".format(li))
#         return None
#
#
# for li in li_list:
#     insert_new_item(li)
#
# for item in items.values():
#     print("title: {0}, price: {1}, image: {2}".format(item.title, item.price, item.image))

#
# print(uls[0].prettify())
# print(uls[0].find())

# ul->li->a->img (src) or ul->li->a->div (class=swipe)->div (class=swipe-wrap)->div->img
# ul->li->a->span (class=result-price)
# ul->li->p->a (class=result-title hdrlink)
# ul->li->p->span (class=result-meta)->span (class=result-price)
# ul->li->p->span (class=result-meta)->span (class=result-hood)


# magnifying_glass = driver.find_element_by_id("js-open-icon")
# if magnifying_glass.is_displayed():
#   magnifying_glass.click()
# else:
#   menu_button = driver.find_element_by_css_selector(".menu-trigger.local")
#   menu_button.click()
#
# search_field = driver.find_element_by_id("site-search")
# search_field.clear()
# search_field.send_keys("Olabode")
# search_field.send_keys(Keys.RETURN)
# assert "Looking Back at Android Security in 2016" in driver.page_source
# print("hello world!")
# driver.close()
