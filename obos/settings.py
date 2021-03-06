# Scrapy settings for obos project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#

BOT_NAME = 'obos'

SPIDER_MODULES = ['obos.spiders']
NEWSPIDER_MODULE = 'obos.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'Obos Alert (+https://github.com/mortenlj/obos-alert)'

DOWNLOAD_DELAY = 1

ITEM_PIPELINES = [
    "obos.pipelines.MatchingPipeline",
    "obos.pipelines.MailPipeline"
]

MAIL_FROM = "scrapy@ibidem.homeip.net"
