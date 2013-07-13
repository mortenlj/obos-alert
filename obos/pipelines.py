# -*- coding: utf-8
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html

from scrapy import log


class MyMatcher(object):
    email = "mortenjo@ifi.uio.no"

    def match(self, item, spider):
        for attr in dir(self):
            if attr.startswith("valid_"):
                validator = getattr(self, attr)
                if not validator(item):
                    return False
        return True

    def valid_location(self, item):
        if item["location_major"] == u"Oslo"and item["location_minor"] == u"Ullern":
            return True
        return False

    def valid_price(self, item):
        return item["total_price"] <= 4000000

    def valid_property_type(self, item):
        return item["property_type"] in (u"Rekkehus", u"Småhus", u"Enebolig")

    def valid_size(self, item):
        return item["size"] > 85

    def valid_rooms(self, item):
        return item["rooms"] >= 4


class MatchingPipeline(object):

    matchers = (
        MyMatcher(),
    )

    def process_item(self, item, spider):
        for matcher in self.matchers:
            if matcher.match(item, spider):
                item.add_email(matcher.email)
        return item
