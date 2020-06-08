__version__ = "0.5"

from urllib.parse import urlparse
import time, sys
import logging
import re

import feedparser
import requests
import emoji
from bs4 import BeautifulSoup
from dateutil import parser
import pytz
from tzlocal import get_localzone

from . import markdownify as md
from . import emojimapper

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class Mercury:

    def __init__(self, config):
        self.RSS_FEED_URL = str(config['rss']['feed_url'])
        self.DISCORD_WEBHOOK_URL = str(config['discord']['webhook_url'])
        self.DISCORD_EMBED_TITLE = str(config['discord']['embed_title']) if 'embed_title' in config['discord'] else False
        self.DISCORD_EMBED_COLOR = False
        if 'embed_color' in config['discord'] and  config['discord']['embed_color']:
            try:
                self.DISCORD_EMBED_COLOR = int(config['discord']['embed_color'])
            except:
                logger.warning("Custom Embed Color: Not a decimal color. Ignoring...")

        self.DISCORD_EMBED_FOOTER_ICON_URL = str(config['discord']['embed_footer_icon_url']) if 'embed_footer_icon_url' in config['discord'] else False

        self.TIMEZONE = get_localzone()
        if 'timezone' in config['general'] and config['general']['timezone']:
            try:
                self.TIMEZONE = pytz.timezone(str(config['general']['timezone']))
            except:
                logger.warning("Invalid Timezone: " + str(config['general']['timezone']) + ". Fallback to the host Timezone...")

        logger.info("Timezone set to: " + str(self.TIMEZONE))

        self.DISCORD_EMBED_SHOW_TZ = False
        if 'show_timezone' in config['discord'] and config['discord']['show_timezone']:
             self.DISCORD_EMBED_SHOW_TZ = str(config['discord']['show_timezone'].lower()[0]) == 'y'

        self.WEBSITES_SETTINGS = {
            "robertsspaceindustries.com": {
                'icon_url': "https://i33.servimg.com/u/f33/11/20/17/41/spectr10.png",
                'dec_color': 2674940,
            },
            "www.reddit.com": {
                'icon_url': "https://2.bp.blogspot.com/-r3brlD_9eHg/XDz5bERnBMI/AAAAAAAAG2Y/XfivK0eVkiQej2t-xfmlNL6MlSQZkvcEACK4BGAYYCw/s1600/logo%2Breddit.png",
                'dec_color': 16729344,
            }
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
            logger.debug("It seems the RSS Feed was modified, but the id of the newest entry hasn't changed. Ignoring...")
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

        # HTML -> Markdown
        body = md.markdownify(soup.prettify(), bullets="-")

        # Max 2 new lines in a row
        body_trimmed = re.sub(r'\n\s*\n', '\n\n', body)

        # For blocquotes too
        # There's probably a simpler way to do this, but I'm too tired to fight with regex :D
        while re.search(r'\n>\s*\n>\s*\n>\s*\n>', body_trimmed, re.MULTILINE):
            body_trimmed = re.sub(r'\n>\s*\n>\s*\n>\s*\n>', '\n> \n> ', body_trimmed)
        body_trimmed = re.sub(r'\n>\s*\n>\s*\n>', '\n> \n> ', body_trimmed)

        # Parse published date
        datetime_published = parser.parse(rss_entry.published)
        datetime_published_tz = datetime_published.astimezone(self.TIMEZONE)

        # Building final Discord Embed JSON
        return {
            "content": self.DISCORD_EMBED_TITLE,
            "embeds": [
                {
                    "description": (body_trimmed[:2044] + '...') if len(body_trimmed) > 2048 else body_trimmed,
                    "color": self.DISCORD_EMBED_COLOR if self.DISCORD_EMBED_COLOR else self.WEBSITES_SETTINGS[urlparse(rss_entry.link).hostname]['dec_color'],
                    "footer": {
                        "icon_url": self.DISCORD_EMBED_FOOTER_ICON_URL,
                        "text": "SC-Devtracker " + __version__ ,
                    },
                    "author": {
                        "name": rss_entry.author,
                        "icon_url": self.WEBSITES_SETTINGS[urlparse(rss_entry.link).hostname]['icon_url']
                    },
                    "fields": [
                        {
                            "name": "Topic",
                            "value": "[" + rss_entry.title + "](" + rss_entry.link + ")"
                        },
                        {
                            "name": "Published",
                            "value": datetime_published_tz.strftime("%e %b %Y %H:%M (UTC%z)") if self.DISCORD_EMBED_SHOW_TZ else datetime_published_tz.strftime("%e %b %Y %H:%M")
                        }
                    ]
                }
            ]
        }

    def _send_json_to_webhook(self, discord_embed_json):
        try:
            response = requests.request("POST", self.DISCORD_WEBHOOK_URL, json=discord_embed_json)
        except requests.RequestException as e:
            logger.critical("Discord Webhook Request failed: " + str(e))
            logger.critical("Closing in 5s...")
            time.sleep(5)
            sys.exit(0)

        if response.status_code != 204:
            logger.warning("Discord Response: " +  response.reason + ' (' + str(response.status_code) + ') ' + " | " + response.text)
            if response.status_code == 400:
                logger.error("Mercury: It seems an invalid JSON was sent, check your config.ini file.")
        else:
            logger.info("Discord Response: Success (" + str(response.status_code) + ")")

    def _replace_emoji_shortcodes(self, rss_entry_body):

        emojis_shortcodes = set(self.emoji_regex.findall(rss_entry_body))
        emojis_shortcodes_to_patch = emojimapper.get_patchable_shortcodes(emojis_shortcodes)

        for shortcode in emojis_shortcodes_to_patch:
            shortcode_converted = emojimapper.get_valid_shortcode(shortcode)
            if shortcode_converted:
                rss_entry_body = rss_entry_body.replace(shortcode, shortcode_converted)
                logger.debug("EmojiConverter: " + shortcode + " -> " + shortcode_converted)

        rss_entry_body_emojized = emoji.emojize(rss_entry_body, use_aliases=True)
    
        unsupported_shortcodes = set(self.emoji_regex.findall(rss_entry_body_emojized))
        if unsupported_shortcodes:
            logger.warning("Unsupported Emojis detected: " + str(unsupported_shortcodes))

        return rss_entry_body_emojized
