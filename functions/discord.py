""" Methods to send messages to discord """
import requests
import global_vars

def send_simple_message(title, description):
    """ Create a basic message to send to discord """
    # Max 2000 characters in the description
    # If it is to long then split it out on the \n
    descriptions = []
    if len(description) < 2000:
        descriptions.append(description)
    else:
        text_left = description
        print('doing loop')
        print(f'start length {len(text_left)}')
        while (len(text_left) > 0):
            print(f'looping text with {len(text_left)}')
            index = text_left.rfind('\n', 0, 2000)
            print(f'found new line at index of {index}')
            if index:
                shortened_text = text_left[0:index]
                print(shortened_text)
                descriptions.append(shortened_text)
                text_left = text_left[index+1:]
            else:
                print(f"skipping text left {len(text_left)}")
                text_left = ""

    embeds = []
    for i in range(len(descriptions)):
        embed_part = {}
        if i == 0:
            embed_part["title"] = title
        embed_part["description"] = descriptions[i]
        embeds.append(embed_part)

    message = {}
    message['embeds'] = embeds
    send_to_discord(message)
    print(f"Message Sent to Discord")

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
    else:
        print("ERROR: Failed to send to discord")
        print(res)
        print(message)
