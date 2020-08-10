""" Methods to send messages to discord """
import requests
import global_vars

def send_simple_message(title, description):
    """ Create a basic message to send to discord """
    message = {}
    first_part = {}
    first_part["title"] = title
    first_part["description"] = description
    message['embeds'] = [first_part]
    send_to_discord(message)

def send_to_discord(message):
    """ Send a preconfigured message to discord """
    # JSON_DATA = json.dumps(MESSAGE)
    res = requests.post(
        global_vars.DISCORD_URL,
        headers={"Content-Type":"application/json"},
        json=message
    )
    if res.status_code == 204:
        print("You should see a message in discord.")
