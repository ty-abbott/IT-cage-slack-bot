import os
import time
import re
from slackclient import SlackClient

#instantiate Slack client
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
slackbot_id = None 

#constants
RTM_READ_DELAY = 1 # 1 second delay between reading from RTM
EXAMPLE_COMMAND = "do"
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"


def parse_bot_commands(slack_events):
    """
        parses a list of events coming from the slack RTM API to find bot commands. 
        If a bot command is found, this function returns a tuple of command and channel. 
        If its not found, this function returns none, none.
    """
    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:
            user_id, message = parse_direct_mention(event["text"])
            if user_id == slackbot_id:
                return message, event["channel"]
    return None, None

def parse_direct_mention(message_text):
    '''
    Finds a direct mention (a mention that is at the beginning) in message text 
    and returns the user ID which was mentioned. If there is no direct mention, returns None
'''
    matches = re.search(MENTION_REGEX, message_text)
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

def handle_command(command, channel):
    """
        executes the bot command if the command is known
    """
    # default response is the help text for the user

    default_response = "Not sure what you mean Try .help for available commmands"

    # finds and executes the given command, filling in response
    response = None
    # this is where we begin to implement new commands
    
    if command.startswith(EXAMPLE_COMMAND):
        response = "Sure... write some more code and then I can do that!"
    
    #sends the response back to the channel
    slack_client.api_call(
        "chat.postMessage", 
        channel=channel,
        text=response or default_response
    )

if __name__ == "__main__":
    if slack_client.rtm_connect(with_team_state=False):
        print("slack bot is up and running")
        # read bots user id by calling web api method "auth.test"
        slackbot_id = slack_client.api_call("auth.test")["user_id"]
        while True:
            command, channel = parse_bot_commands(slack_client.rtm_read())
            if command:
                handle_command(command, channel)
            time.sleep(RTM_READ_DELAY)
    else:
        print("connection failed. exception to traceback printed above.")
    
