import boto3
from botocore.exceptions import ClientError

def get_secret():
    secret_name = "igcred"
    region_name = "ap-southeast-2"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e

    raw_secret_response = get_secret_value_response['SecretString']
    secret_response = json.loads(raw_secret_response)
    username = secret_response['username']
    password = secret_response['password']
    return username, password

import json
import time
from instagrapi import Client
from instagrapi.exceptions import LoginRequired
import logging

logger = logging.getLogger()

filepath='/home/ec2-user/proj-espresso/bookmarks.json'
sessionpath='/home/ec2-user/proj-espresso/session.json'

# Load bookmarks
def load_bookmarks(filepath=filepath):
    with open(filepath, 'r') as file:
        return json.load(file)

# Overwrite bookmarks
def save_bookmarks(filepath, data):
    """Save JSON data to a file."""
    with open(filepath, 'w') as file:
        json.dump(data, file, indent=4)

def remove_entry_by_url(filepath, target_url):
    """Remove an entry from the JSON file if the URL matches."""
    data = load_bookmarks(filepath)
    if 'reels' in data:
        original_length = len(data['reels'])
        data['reels'] = [entry for entry in data['reels'] if entry['url'] != target_url]
        new_length = len(data['reels'])
        if new_length < original_length:
            print(f"Removed {original_length - new_length} entry(ies) with URL: {target_url}")
        else:
            print(f"No entries found with URL: {target_url}")
    else:
        print("No 'reels' key found in JSON data.")
    save_bookmarks(filepath, data)

# Login to Instagram
def instagram_login(username, password):
    cl = Client()
    session = False
    try:
        cl.load_settings(sessionpath)
    except FileNotFoundError:
        session = False
    
    print(session)
    login_via_session = False
    login_via_pw = False

    if session:
        try:
            cl.set_settings(session)
            cl.login(username, password)

            # check if session is valid
            try:
                cl.get_timeline_feed()
            except LoginRequired:
                logger.info("Session is invalid, need to login via username and password")

                old_session = cl.get_settings(sessionpath)

                # use the same device uuids across logins
                cl.set_settings({})
                cl.set_uuids(old_session["uuids"])

                cl.login(username, password)
            login_via_session = True
        except Exception as e:
            logger.info("Couldn't login user using session information: %s" % e)

    if not login_via_session:
        try:
            logger.info("Attempting to login via username and password. username: %s" % username)
            if cl.login(username, password):
                login_via_pw = True
                cl.dump_settings(sessionpath)
        except Exception as e:
            logger.info("Couldn't login user using username and password: %s" % e)

    if not login_via_pw and not login_via_session:
        raise Exception("Couldn't login user with either password or session")

    return cl

# Send Reel via DM
def send_reel_dm(client, reel_url, recipient_user_id):
    media_pk = client.media_pk_from_url(reel_url)
    success = client.direct_media_share(media_pk, [recipient_user_id])
    if success:
        remove_entry_by_url(filepath, reel_url)

# Main function
def main():
    # Load bookmarks
    bookmarks = load_bookmarks()

    # Instagram credentials
    username, password = get_secret()

    # Login to Instagram
    client = instagram_login(username, password)

    # get user_id
    # f"https://www.instagram.com/web/search/topsearch/?query={username}"

    # Iterate over bookmarks and send each Reel via DM
    reel_url = bookmarks['reels'][0]["url"]
    recipient_user_id = ""
    send_reel_dm(client, reel_url, recipient_user_id)
    time.sleep(2)  # To avoid spamming and being flagged by Instagram

if __name__ == "__main__":
    main()