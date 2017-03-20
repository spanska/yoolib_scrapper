#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unicodedata
from urllib.parse import urlparse, urlunparse

import piexif
import requests
import scrapy

URL = "http://my.yoolib.com/mht/collection/?esp=0"

DATA_DIR = "/home/jean-baptiste/mht_files"

WIDTH = 1024

HEIGHT = 640

TRANSLATE_TABLE = {
    "\xa0": "Dimensions du document"
}


class ThumbnailsSpider(scrapy.Spider):
    FILENAME_TRANS_TAB = str.maketrans(*["/\0", "__"])

    name = "thumbnails"
    start_urls = [URL]

    def parse(self, response):
        nav_selector = '.wp-pagenavi a::attr(href)'
        next_page_url = response.css(nav_selector).extract()[-1]

        for media_url in self.parse_result_page(response):
            yield scrapy.Request(
                response.urljoin(media_url),
                callback=self.parse_media_page
            )

        if not response.url.endswith(next_page_url):
            yield scrapy.Request(
                response.urljoin(next_page_url),
                callback=self.parse
            )

    def parse_result_page(self, response):
        title_selector = 'h2.title'
        for brickset in response.css(title_selector):
            yield brickset.css("a::attr(href)").extract_first()

    def parse_media_page(self, response):

        infos = {"scrapper_url": response.url}

        title_selector = '//h1[@class="title"]/text()'
        infos['titre'] = response.xpath(title_selector).extract_first()

        media_infos_selector = '#media_info'
        media_infos = response.css(media_infos_selector).extract_first()

        infos['description'] = scrapy.Selector(text=media_infos).xpath('//p/text()').extract_first()

        extra_infos = scrapy.Selector(text=media_infos).css('.itembloc1').extract()

        for extra_info in extra_infos:
            selector = scrapy.Selector(text=extra_info)

            key = selector.xpath('//div[@class="keybloc1"]/text()').extract_first()
            if key in TRANSLATE_TABLE:
                key = TRANSLATE_TABLE[key]

            text_value = selector.xpath('//div[@class="valuebloc1"]/text()').extract_first()
            link_value = selector.xpath('//div[@class="valuebloc1"]/a/text()').extract_first()

            infos[key] = text_value or link_value

        img_src_selector = '#yoolib_img img::attr(src)'
        img_src = response.css(img_src_selector).extract_first()
        parsed_url = list(urlparse(img_src))
        params = [x for x in parsed_url[4].split('&') if not (x.startswith('WID') or x.startswith('HEI')
                                                              or x.startswith('CVT'))]
        params.extend(["WID=" + str(WIDTH), "HEI=" + str(HEIGHT), "CVT=JPEG"])
        parsed_url[4] = '&'.join(params)

        ThumbnailsSpider.write_and_tag_picture(urlunparse(parsed_url), infos)

    @staticmethod
    def write_and_tag_picture(picture_url, media_infos):

        file_name = DATA_DIR + '/' + media_infos['titre'].translate(ThumbnailsSpider.FILENAME_TRANS_TAB) + '.jpeg'

        with open(file_name, 'wb') as handle:
            response = requests.get(picture_url, stream=True)
            for block in response.iter_content(1024):
                handle.write(block)

        exif_datas = piexif.load(file_name)
        exif_datas['Exif'][piexif.ExifIFD.UserComment] = ThumbnailsSpider._remove_accents(str(media_infos))
        exif_bytes = piexif.dump(exif_datas)
        piexif.insert(exif_bytes, file_name)

    @staticmethod
    def _remove_accents(input_str):
        nfkd_form = unicodedata.normalize('NFKD', input_str)
        only_ascii = nfkd_form.encode('ASCII', 'ignore')
        return only_ascii
