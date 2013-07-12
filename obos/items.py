# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html
from datetime import datetime, timedelta

from scrapy.contrib.loader import XPathItemLoader
from scrapy.contrib.loader.processor import TakeFirst
from scrapy.item import Item, Field

import re

class AsInt(object):
    _pattern = re.compile(r"\D")

    def __call__(self, it):
        for v in it:
            if not v:
                continue
            digs = self._pattern.sub("", v)
            if not digs:
                continue
            return int(digs)


class BaseAsDateTime(object):
    FORMAT = ""

    def __call__(self, it):
        return self.get_datetime(it)

    def prepare_value(self, v):
        return v

    def get_datetime(self, it):
        for v in it:
            if v:
                try:
                    return datetime.strptime(self.prepare_value(v), self.FORMAT)
                except ValueError:
                    pass


class AsDate(BaseAsDateTime):
    FORMAT = "%d.%m.%Y"

    def __call__(self, it):
        dt = self.get_datetime(it)
        return dt.date()

    def prepare_value(self, v):
        if u"intern" in v:
            return u"01.01.1900"
        return v


class AsDateTime(BaseAsDateTime):
    FORMAT = "%d.%m.%Y kl %H.%M"

    def __call__(self, it):
        self._inc_date = False
        datetime = self.get_datetime(it)
        if self._inc_date:
            datetime = datetime + timedelta(days=1)
        return datetime

    def prepare_value(self, v):
        w = v.replace("kl 24.00", "kl 00.00")
        self._inc_date = w != v
        return w


class ObosItem(Item):
    location_major = Field()
    location_minor = Field()
    address = Field()
    rooms = Field(input_processor=AsInt())
    size = Field(input_processor=AsInt())
    property_type = Field()
    price = Field(input_processor=AsInt())
    debt = Field(input_processor=AsInt())
    total_price = Field(input_processor=AsInt())
    deadline = Field(input_processor=AsDateTime())
    current_seniority = Field(input_processor=AsDate())
    link = Field()


class ObosLoader(XPathItemLoader):
    default_output_processor = TakeFirst()
    default_item_class = ObosItem

    rooms_and_property_pattern = re.compile(r"(\d+)-roms (\S+)")

    def add_rooms_and_property_type(self, xpath):
        values = self._get_values(xpath)
        for value in values:
            m = self.rooms_and_property_pattern.search(value)
            if m:
                self.add_value("rooms", m.group(1))
                self.add_value("property_type", m.group(2))

