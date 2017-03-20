#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from urllib.parse import urlparse

import requests
import scrapy

URLS = [
    "http://my.yoolib.com/mht/collection/2008-yacht-auxiliaire-de-10-5-metres/?n=2131"
]

DATA_DIR = "/home/jean-baptiste/mht_files"


TRANSLATE_TABLE = {
    "\xa0": "Dimensions du document"
}


class PictureSpider(scrapy.Spider):
    FILENAME_TRANS_TAB = str.maketrans(*["/\0", "__"])

    name = "picture"
    start_urls = URLS

    def parse(self, response):

        title_selector = '//h1[@class="title"]/text()'
        title = response.xpath(title_selector).extract_first()

        img_src_selector = '#yoolib_img img::attr(src)'
        img_src = response.css(img_src_selector).extract_first()
        parsed_url = urlparse(img_src)

        pos = parsed_url.query.find("FIF=")
        pos_2 = parsed_url.query.find("&", pos)

        if pos != -1:

            file_url = parsed_url.query[pos + 4: pos_2 if pos_2 != -1 else len(parsed_url.query)]
            download_url = "http://" + parsed_url.netloc + file_url
            PictureSpider.download_picture(download_url, title)

        else:
            raise Exception("Parameter FIF not found")

    @staticmethod
    def download_picture(picture_url, title):

        file_name = DATA_DIR + '/' + title.translate(PictureSpider.FILENAME_TRANS_TAB) + '.tif'

        with open(file_name, 'wb') as handle:
            response = requests.get(picture_url, stream=True)
            for block in response.iter_content(1024):
                handle.write(block)
