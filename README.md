# SC-Devtracker

A simple **RSS/Discord Webhook connector** written in **Python 3**.

![SC Devracker Discord Embed](https://i.imgur.com/UZM4A71.png)

## Description

The [RSS Feed](https://developertracker.com/star-citizen/rss) from [Developer Tracker](https://developertracker.com) is feeding posts whenever a Star Citizen developer post anything on [Spectrum](https://robertsspaceindustries.com/spectrum/community/SC) or the [Star Citizen Subreddit](https://www.reddit.com/r/starcitizen/).

[SC-Devtracker](https://github.com/arbaes/sc-devtracker) monitors that feed, parse the latest entry and then send it to the pre-configured [Discord Webhook](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks).

## Requirements

* Python 3.7<sup>[[1]](#footnotes)</sup>

**SC-Devtracker** needs the following **python packages** to work properly:

* configparser
* feedparser
* requests
* beautifulsoup4
* six

## Installation

* **Clone** this repository wherever you like:
  
```shell
git clone git@github.com:s0me-1/sc-devtracker.git
```

* Install the **requirements** if you haven't already satisfied them:

```shell
pip install -r requirements.txt
```

* Create a [Discord Webhook](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks&amp?page=3).
* Complete your `config.ini` file (See [Configuration](#configuration)).

## Usage

**Any Platform**
Once a proper `config.ini` is created, simply run:

```shell
python -m sc-devtracker
```

**Linux**
Alternatively, you can run:

```bash
./start.sh
```

**Windows**
Execute `start.bat`

## Configuration

Complete `config-exemple.ini` and then rename it to `config.ini`.
Here's a description of what you can put there:

* `feed_url`: A valid RSS Feed, defaulted to the one from [developertracker.com](https://developertracker.com/star-citizen/rss).
* `webhook_url`: A valid url pointing to a discord webhook. This is what you need to complete.
* `embed_color`: A color for the embed border in discord. Must be in decimal format.
* `footer_icon_url`: Icon displayed in the footer of the discord embeds.
* `fetch_delay`: The time in seconds between each refresh of the RSS Feed.
* `locale` (Optionnal): The locale used to display the published time of each entry, use the one on the host by default. Must follow the `xx_XX` format and must be installed on the host machine.

This is the content of `config-sample.ini`:

```ini
[rss]
feed_url = https://developertracker.com/star-citizen/rss

[discord]
webhook_url = YOUR_WEBHOOK_URL
embed_color = 16750848
footer_icon_url = https://i33.servimg.com/u/f33/11/20/17/41/zer0110.png

[general]
fetch_delay = 60
locale = en_US
```

## Credits

* [BeautifulSoup 4](https://www.crummy.com/software/BeautifulSoup/)
* [Requests](https://requests.readthedocs.io/en/master/)
* [Jason R. Coombs](https://github.com/jaraco/) for **[configparser](https://github.com/jaraco/configparser/)**
* [Kurt McKee](https://github.com/kurtmckee) for **[feedparser](https://github.com/kurtmckee/feedparser)**.
* [Matthew Dapena-Tretter](https://github.com/matthewwithanm/) for **[markdownify](https://github.com/matthewwithanm/python-markdownify)**<sup>[[2]](#footnotes)</sup>

## License

[GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.en.html)

## Footnotes

* <sup>[1]</sup> **python-feedparser** currently needs to be updated to properly support Python 3.8.
* <sup>[2]</sup> The version used in **SC-Devtracker** is an unofficial version that includes a patch for handling blocquotes properly.
