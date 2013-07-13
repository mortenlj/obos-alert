# -*- coding: utf-8
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html

from scrapy import log
from scrapy.mail import MailSender
from scrapy.conf import settings


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
        if item["location_major"] == u"Oslo"and item["location_minor"] == u"Nordstrand":
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


MAIL_BODY_TEMPLATE = u"""
%(location_major)s / %(location_minor)s
=======================================

Adresse: %(address)s
Areal: %(size)s
Boligtype: %(property_type)s
Antall rom: %(rooms)s
Pris: %(price)s
Fellesgjeld: %(debt)s
Totalpris: %(total_price)s

Meldefrist: %(deadline)s
Ansiennitet pt: %(current_seniority)s
"""

class MailPipeline(object):
    def __init__(self):
        self.mailer = MailSender.from_settings(settings)

    def process_item(self, item, spider):
        if item.get_emails():
            log.msg("Sending mail to %s for %s" % (item.get_emails(), item), level=log.INFO)
            self.mailer.send(list(item.get_emails()), u"OBOS Alert", self.create_body(item))
        return item

    def create_body(self, item):
        return (MAIL_BODY_TEMPLATE % item).encode("us-ascii", "replace") # Only supported encoding! https://github.com/scrapy/scrapy/issues/348
