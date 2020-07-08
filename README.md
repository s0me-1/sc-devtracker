# Star Citizen Discord Devtracker (SC-Devtracker)

A simple **RSS/Discord Webhook connector** written in **Python 3**.

![SC Devtracker Discord Embed Scpectrum](https://i.imgur.com/z7X9vpR.png)
![SC Devtracker Discord Embed Reddit](https://i.imgur.com/vVeauBE.png)

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
* emoji
* pytz
* python-dateutil
* tzlocale

## Installation

* Download the latest [Release](https://github.com/s0me-1/sc-devtracker/releases/).

**or**

* Clone this repository wherever you like (Maybe unstable).

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

Once properly started, **SC-Devtracker** will fetch and send the most recent entry of the RSS Feed to ensure everything is working as expected.

**Linux**

Run in shell:
```bash
./start.sh
```

---

Run as a systemd service:

Considering your installation is in **/opt/sc-devtracker** and the user running this unit is **discord**.

create a symlink of sc-devtracker.service in /etc/systemd/system/
```bash
ln -s /opt/sc-devtracker/sc-devtracker.service /etc/systemd/system/
```

reload systemd:
```bash
systemctl daemon-reload
```

enable the service and start it:
```bash
systemctl enable sc-devtracker
systemctl start sc-devtracker
```


**Windows**

Execute `start.bat`

## Configuration

Complete `config-exemple.ini` and then rename it to `config.ini`.
Here's a description of what you can put there:

* `feed_url`: A valid RSS Feed, defaulted to the one from [developertracker.com](https://developertracker.com/star-citizen/rss).
* `webhook_url`: A valid url pointing to a discord webhook. This is what you need to complete.
* `embed_title` (Optionnal): Discord message title displayed each time an embed is sent.
* `embed_color` (Optionnal): A decimal color for the embed border in discord. Defaults selects a color depending on the source website (Light Blue for Spectrum, Orange for Reddit).
* `embed_footer_icon_url`: Icon displayed in the footer of the discord embeds.
* `show_timezone` (Optionnal): If set to Yes, it will show the timezone in UTC Format (See below). Defaults to No.
  ![Without show_timezone](https://i.imgur.com/kC8IOs0.png) ![With show_timezone](https://i.imgur.com/FbRj0CD.png)
* `fetch_delay` (Optionnal): The time in seconds between each refresh of the RSS Feed. Defaults to **600** as the RSS Feed is only updated every 10 minutes.
* `locale` (Optionnal): The locale used to display the published time of each entry, use the one on the host by default. Must follow the `xx_XX` format and must be installed on the host machine.
* `timezone` (Optionnal): Desired timezone for published dates. Must be a valid [pytz Timezone](https://gist.github.com/heyalexej/8bf688fd67d7199be4a1682b3eec7568).

This is the content of `config-sample.ini`:

```ini
[rss]
feed_url = https://developertracker.com/star-citizen/rss

[discord]
webhook_url = YOUR_WEBHOOK_URL
embed_title = New post from a SC Dev !
embed_color =
embed_footer_icon_url = https://avatars2.githubusercontent.com/u/7307512
show_timezone =

[general]
fetch_delay =
locale =
timezone =
```

## Future Feature

* Better parsing of the HTML content by getting it directly from the source websites

## Known Bugs

* DOM coming from the RSS source maybe incorrect (Especially with lists), resulting in excessive new line in some lists after parsing.
* Code block are not supported by the RSS feed, therefore, they will not show in the discord embed.

## Credits

* [BeautifulSoup 4](https://www.crummy.com/software/BeautifulSoup/).
* [Requests](https://requests.readthedocs.io/en/master/).
* [Jason R. Coombs](https://github.com/jaraco/) for **[configparser](https://github.com/jaraco/configparser/)**.
* [Kurt McKee](https://github.com/kurtmckee) for **[feedparser](https://github.com/kurtmckee/feedparser)**.
* [Matthew Dapena-Tretter](https://github.com/matthewwithanm/) for **[markdownify](https://github.com/matthewwithanm/python-markdownify)**<sup>[[2]](#footnotes)</sup>.
* [Taehoon Kim](https://github.com/carpedm20) & [Kevin Wurster](https://github.com/geowurster) for **[emoji](https://github.com/carpedm20/emoji)**.

## License

[GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.en.html)

## Footnotes

* <sup>[1]</sup> **python-feedparser** currently needs to be updated to properly support Python 3.8.
* <sup>[2]</sup> The version used in **SC-Devtracker** is an unofficial version that includes a patch for handling blocquotes properly.
