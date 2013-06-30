# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

from scrapy.item import Item, Field

class ObosItem(Item):
    location = Field()
    rooms = Field()
    area = Field()
    property_type = Field()
    price = Field()
    debt = Field()
    total_price = Field()
    deadline = Field()
    current_seniority = Field()
