from urllib.parse import urlparse
import locale, sched, time, logging
import sys, os
import configparser
from . import mercury

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

os.chdir(os.path.dirname(__file__))
config = configparser.ConfigParser()
try:
    config.read('../config.ini')
except:
    logger.critical("Invalid 'config.ini' file !")
    logger.critical("Closing in 5s...")
    time.sleep(5)
    sys.exit(0)


if not config.sections():
    logger.critical("No 'config.ini' file detected !")
    logger.critical("Closing in 5s...")
    time.sleep(5)
    sys.exit(0)

# Set delay between fetches
FEED_PARSE_DELAY = 60
if 'fetch_delay' in config['general'] and config['general']['fetch_delay']:
    try:
        FEED_PARSE_DELAY = int(config['general']['fetch_delay'])
    except:
        logger.warning("Custom Fetch Delay: Invalid value. Fallback to 60 as default...")

# Set Custom locales if defined
if 'locale' in config['general'] and  config['general']['locale']:
    try:
        # .UTF-8 Needed for Unix Systems
        locale.setlocale(locale.LC_TIME, config['general']['locale'] + ".UTF-8")
    except Exception as e:
        logger.warning("Locale: " + str(e) + " - Fallback to OS default...")

mercury = mercury.Mercury(config)

def star_runner(sc):
    """ Check for new RSS Post every FEED_PARSE_DELAY
    and send the last new entry to the set discord webhook
    """
    new_posts = mercury._get_last_rss_posts()
    if new_posts:
        logger.info('Retrieved ' + str(len(new_posts)) + ' post(s) to send.')
        for post in new_posts:
            logger.info('Sending: "' + post.title + '" [' + urlparse(post.link).hostname + ']')
            discord_embed = mercury._generate_discord_json(post)
            mercury._send_json_to_webhook(discord_embed)
            # Prevent discord rate limiting
            time.sleep(2)
    s.enter(FEED_PARSE_DELAY, 1, star_runner, (sc,))

s = sched.scheduler(time.time, time.sleep)
s.enter(0, 1, star_runner, (s,))
s.run()
