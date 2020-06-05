from urllib.parse import urlparse
import time
import logging
import re

import feedparser
import requests
import emoji
from bs4 import BeautifulSoup

from . import markdownify as md
from . import emojiconverter

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class Mercury:

    def __init__(self, config):
        self.RSS_FEED_URL = str(config['rss']['feed_url'])
        self.DISCORD_WEBHOOK_URL = str(config['discord']['webhook_url'])
        self.DISCORD_EMBED_COLOR = int(config['discord']['embed_color'])
        self.DISCORD_EMBED_FOOTER_ICON_URL = str(config['discord']['footer_icon_url'])
        self.ICON_URLS = {
            "robertsspaceindustries.com": "https://i33.servimg.com/u/f33/11/20/17/41/spectr10.png",
            "www.reddit.com": "https://2.bp.blogspot.com/-r3brlD_9eHg/XDz5bERnBMI/AAAAAAAAG2Y/XfivK0eVkiQej2t-xfmlNL6MlSQZkvcEACK4BGAYYCw/s1600/logo%2Breddit.png"
        }

        self.emoji_regex =  re.compile(r":[a-z]+(?:_[a-z]+)*:", re.MULTILINE)

        self.feed_last_modified = False
        self.last_entry_id = False
        logger.info('Mercury initialized successfully')

    def _check_last_rss_post(self):
        logger.debug("Fetching RSS Feed...")
        feed_update = feedparser.parse(self.RSS_FEED_URL, modified=self.feed_last_modified)

        # 304 means no new entries
        if feed_update.status == 304:
            logger.debug("RSS Feed wasnt modified since last check.")
            return False
        self.feed_last_modified = feed_update.modified
        
        # Prevent sending the same entry twice
        if self.last_entry_id == feed_update.entries[0].id:
            logger.debug("It seems the RSS Feed was modified, but the id of the newest entry hasn't changed.")
            return False
        self.last_entry_id = feed_update.entries[0].id

        logger.debug('New entry found: ' + feed_update.entries[0].title)
        return feed_update.entries[0]

    def _generate_discord_json(self, rss_entry):
        rss_sumary_emoji_converted = self._replace_emoji_shortcodes(rss_entry.summary)
        soup = BeautifulSoup(rss_sumary_emoji_converted, "html.parser")

        # Fix blockquote from Spectrum
        for quoteauthor in soup.find_all('div', {'class': 'quoteauthor'}):
            quoteauthor.insert_after(soup.new_tag("br"))
            quoteauthor.insert_after(soup.new_tag("br"))
            quoteauthor.insert_after(":")

        # Fix blockquote from Reddit
        for quoteauthor in soup.find_all('div', {'class': 'bb_quoteauthor'}):
            quoteauthor.insert_after(soup.new_tag("br"))
            quoteauthor.insert_after(soup.new_tag("br"))
            quoteauthor.insert_after(":")

        body = md.markdownify(soup.prettify(), bullets="-")
        body_trimmed = re.sub(r'\n\s*\n', '\n\n', body)

        # Check the conversion result
        logger.debug(soup.prettify())
        logger.debug(body_trimmed)

        return {
            "embeds": [
                {
                    "description": (body_trimmed[:2044] + '...') if len(body_trimmed) > 2048 else body_trimmed,
                    "color": self.DISCORD_EMBED_COLOR,
                    "footer": {
                        "icon_url": self.DISCORD_EMBED_FOOTER_ICON_URL,
                        "text": time.strftime("%e %b %Y | %H:%M", rss_entry.published_parsed),
                    },
                    "author": {
                        "name": rss_entry.author,
                        "icon_url": self.ICON_URLS[urlparse(rss_entry.link).hostname]
                    },
                    "fields": [
                        {
                        "name": "Topic",
                        "value": "[" + rss_entry.title + "](" + rss_entry.link + ")"
                        }
                    ]
                }
            ]
        }

    def _send_json_to_webhook(self, discord_embed_json):
        response = requests.request("POST", self.DISCORD_WEBHOOK_URL, json=discord_embed_json)
        logger.info("Discord Response: " + str(response.status_code))
        logger.debug(response.reason + " | " + response.text)

    def _replace_emoji_shortcodes(self, rss_entry_body):

        emojis_shortcodes = set(self.emoji_regex.findall(rss_entry_body))
        for shortcode in emojis_shortcodes:
            shortcode_converted = emojiconverter.get_converted_sc(shortcode)
            if shortcode_converted:
                rss_entry_body = rss_entry_body.replace(shortcode, shortcode_converted)
                logger.debug("EmojiConverter: " + shortcode + " -> " + shortcode_converted)
            else:
                logger.debug("EmojiConverter: No entry for " + str(shortcode) + ". Skipping...")

        return emoji.emojize(rss_entry_body, use_aliases=True)
