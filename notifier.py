#!/usr/bin/env python3

import shelve
import logging
import requests
import json
from http.client import responses
from threading import Timer

import yaml
import feedparser

API_ENDPOINT = "https://api.pushover.net/1/messages.json"
CONFIG_FILE = "config.yml"
DATA_FILE   = "data"

logging.basicConfig(level=logging.INFO)

def validate_config(config_file):
    """Validates YAML configuration file, returning the data in 
    the config file."""
    logging.info(f"Loading config file {config_file}...")
    try:
        with open(config_file, "r") as cfg:
            config_data = yaml.safe_load(cfg)
    except FileNotFoundError:
        logging.error(f"Could not find configuration file {config_file}!")
        exit(1)
    except PermissionError:
        logging.error(f"Could not read configuration file {config_file}!")
        exit(1)
    if "list_url" not in config_data:
        logging.error(f"Please place the RSS URL in {config_file} under list_url.")
        exit(1)
    if "api_key" not in config_data:
        logging.error(f"Please place the Pushover API key in {config_file} under api_key.")
        exit(1)
    if "user_key" not in config_data:
        logging.error(f"Please place the Pushover user key in {config_file} under user_key.")
        exit(1)
    if "check_interval" not in config_data:
        logging.error(f"Please place the monitoring interval in {config_file} under check_interval.")
        exit(1)
    
    return config_data

def send_notification(api_key, user_id, feed_item):
    """Sends a Pushover notification with the content
    determined by the given feed item."""
    logging.info("Sending push notification...")

    request_body = {
        "token": api_key,
        "user": user_id,
        "message": feed_item["title"],
        "title": "New Novel Updates Chapter",
        "url": feed_item["link"],
        "url_title": "Read Now"
    }

    response = requests.post(API_ENDPOINT, json=request_body)
    code_msg = responses[response.status_code]
    if response.status_code != 200:
        logging.error(f"Push failed.")

    logging.info(f"Got {response.status_code}: {code_msg}")
    response_body = response.json()
    if response_body["status"] != 1:
        logging.error(f"Push request {response_body['request']} failed, got nonzero status. Errors: {response_body['errors']}")
        return

    logging.info(f"Push request {response_body['request']} succeeded.")


def check_feed(url):
    """Checks the RSS feed for new entries. Returns a list of
    feed items."""
    logging.info(f"Checking feed from {url}...")
    new_entries = []
    parsed_feed = feedparser.parse(url)
    if parsed_feed.status != 200:
        logging.error(f"Feed URL returned {parsed_feed.status}, aborting.")
        return new_entries
    logging.info(f"Feed last built at {parsed_feed.feed.updated}.")

    logging.info("Comparing against old data...")
    data = shelve.open(DATA_FILE, writeback=True)
    if 'feed' not in data:
        logging.info("No previous data. Saving...")
        data['feed'] = parsed_feed
        return new_entries

    old_data = data['feed']
    last_updated = data['feed'].feed.updated_parsed
    if not parsed_feed.feed.updated_parsed > last_updated:
        logging.info("Build date hasn't changed, returning.")
        return new_entries
    
    for item in parsed_feed.entries:
        if item['updated_parsed'] > last_updated:
            logging.info(f'New feed item: {item["title"]}')
            new_entries.append(item)
    logging.info("New feed data. Saving...")
    data['feed'] = parsed_feed
    data.close()
    return new_entries

def check_and_notify(config_data):
    """Checks feed for new items, then sends push notification for each."""
    new_entries = check_feed(config_data['list_url'])
    for entry in new_entries:
        send_notification(config_data['api_key'], config_data['user_key'], entry)

def dispatch(config_data):
    """Schedules a feed check to run periodically."""
    logging.info("Dispatching...")
    check_and_notify(config_data)
    t = Timer(
        config_data['check_interval'] * 60.0, # interval is in minutes
        dispatch,
        args=[config_data]
    )
    t.start()

def main():
    config_data = validate_config(CONFIG_FILE)
    dispatch(config_data)

if __name__ == "__main__":
    main()
