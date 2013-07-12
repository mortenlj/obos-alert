import re
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector
from scrapy.spider import BaseSpider
from urlparse import urlparse, urlunparse
from obos.items import ObosLoader


class ObosSpider(BaseSpider):
    name = 'obos'
    allowed_domains = ['obos.no']
    start_urls = ['http://www.obos.no/boliger-med-forkjopsrett']

    rules = (
        (r'boliger-med-forkjopsrett\?p=\d+', "parse_result"),
        (r'boligmedforkjopsrett\?id=\d+', "parse_item"),
    )

    _LOCATION_PATTERN = re.compile(r"(.*?) / (.*?), .*")

    _BULLET_MAPPING = {
        u'Adresse:': "address",
        u'Areal:': "size",
        u'Prisantydning:': "price",
        u'Fastpris:': "price",
        u'Fellesgjeld:': "debt",
        u'Totalpris:': "total_price",
        u'Meldefrist:': "deadline",
        u'Ansiennitet pt:': "current_seniority"
    }

    def __init__(self, **kwargs):
        super(ObosSpider, self).__init__(**kwargs)
        self._rules = []
        self._seen = set()
        for pattern, handler in self.rules:
            rule = (
                re.compile(pattern),
                getattr(self, handler)
            )
            self._rules.append(rule)

    def _create_url_from_anchor(self, base_parse, anchor):
        href = anchor.select("@href").extract()[0]
        anchor_parse = urlparse(href)
        return urlunparse((base_parse.scheme, base_parse.netloc, anchor_parse.path, anchor_parse.params, anchor_parse.query, anchor_parse.fragment))

    def parse_result(self, anchor, url):
        return Request(url)

    def parse(self, response):
        base_parse = urlparse(response.url)
        hxs = HtmlXPathSelector(response)
        anchors = hxs.select("//a[@href]")
        for anchor in anchors:
            url = self._create_url_from_anchor(base_parse, anchor)
            if url in self._seen:
                continue
            self._seen.add(url)
            for pattern, handler in self._rules:
                if pattern.search(url):
                    yield handler(anchor, url)

    def parse_item(self, anchor, url):
        info_cell = anchor.select("../../td[not(@class)]")
        link_text = info_cell.select("a/text()").extract()[0]
        m = self._LOCATION_PATTERN.search(link_text)
        return Request(url,
                       callback=self.parse_item_page,
                       meta={"location_major": m.group(2), "location_minor": m.group(1)}
        )

    def parse_item_page(self, response):
        hxs = HtmlXPathSelector(response)
        panels = hxs.select("//div[@id=\"ctl00_body_PanelDetails\"]")
        loader = ObosLoader(selector=panels, response=response)
        for bullet, field_name in self._BULLET_MAPPING.iteritems():
            loader.add_xpath(field_name, self._build_bullet_path(bullet))
        rooms_and_property_type_xpath = self._build_bullet_path(u'Boligtype:')
        loader.add_rooms_and_property_type(rooms_and_property_type_xpath)
        loader.add_value("link", response.url)
        for field in ("location_major", "location_minor"):
            loader.add_value(field, response.meta[field])
        return loader.load_item()

    def _build_bullet_path(self, bullet):
        return u"dl/dt[text()='%s']/../dd/text()" % bullet