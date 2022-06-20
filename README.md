# novelupdates-notifier
Periodically checks a Novel Updates reading list for changes and pushes notifications to Pushover.

## Setup

Requires Python 3, an account on Pushover with at least one licensed device. Start by creating an account on [Pushover](https://pushover.net/), registering a device, then [registering an application](https://pushover.net/apps/build), and the [RSS feed for your reading list](#rss-link).

Clone this repository:
```console
git clone https://github.com/centipeda/novelupdates-notifier
cd novelupdates-notifier
```
Install Python dependencies:
```console
python3 -m pip install pyyaml feedparser
```

Create your config file:
```console
cp sample_config.yml config.yml
vi config.yml
```

Fill out the following fields with your Pushover API and user key, as well as your RSS feed link:
```yaml
list_url: "https://rssnovelupdates.com/rss.php/uid=XXXXX&type=XXX&idlid=XXX"
api_key:  "azGDORePK8gMaC0QOYAMyEEuzJnyUi"
user_key: "uQiRzpo4DXghDmr9QzzfQu27cmVRsG"
check_interval: 30
```

`check_interval` can be set to any number (in minutes), but if you set it too low you may or may not get rate-limited by Novel Updates or Pushover.

## Running
`notifier.py` can be run like any other Python script. It automatically repeats the check every `check_interval` minutes.

```console
python3 notifier.py
```
or
```console
./notifier.py
```

Since I run `notifier.py` as a service using [PM2](https://pm2.keymetrics.io/), a sample `ecosystem.config.js` is included. That way, you can run

```console
pm2 start
```

and it should run in the background, self-restarting on failure.

## RSS Link

To get your reading list in RSS feed form, click the purple icon above your list next to "List Settings":

![image](https://user-images.githubusercontent.com/16915320/174507015-a811a2e2-fbfe-4aeb-a139-f44df4fc2309.png)

And copy the URL that it sends you to:

![image](https://user-images.githubusercontent.com/16915320/174507057-1292cae6-b3b5-4128-a3b0-b714156a64ca.png)

