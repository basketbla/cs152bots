from enum import Enum, auto
import discord
import re

class State(Enum):
    REPORT_START = auto()
    AWAITING_MESSAGE = auto()
    MESSAGE_IDENTIFIED = auto()
    REPORT_COMPLETE = auto()
    AWAITING_GROUP = auto()
    ACTION_CHOSEN = auto()

class Report:
    START_KEYWORD = "report"
    CANCEL_KEYWORD = "cancel"
    HELP_KEYWORD = "help"

    def __init__(self, client):
        self.state = State.REPORT_START
        self.client = client
        self.message = None
    
    async def handle_message(self, message):
        '''
        This function makes up the meat of the user-side reporting flow. It defines how we transition between states and what 
        prompts to offer at each of those states. You're welcome to change anything you want; this skeleton is just here to
        get you started and give you a model for working with Discord. 
        '''

        if message.content == self.CANCEL_KEYWORD:
            self.state = State.REPORT_COMPLETE
            return ["Report cancelled."]
        
        if self.state == State.REPORT_START:
            reply =  "Thank you for starting the reporting process. "
            reply += "Say `help` at any time for more information.\n\n"
            reply += "Please copy paste the link to the message you want to report.\n"
            reply += "You can obtain this link by right-clicking the message and clicking `Copy Message Link`."
            self.state = State.AWAITING_MESSAGE
            return [reply]
        
        if self.state == State.AWAITING_MESSAGE:
            # Parse out the three ID strings from the message link
            m = re.search('/(\d+)/(\d+)/(\d+)', message.content)
            if not m:
                return ["I'm sorry, I couldn't read that link. Please try again or say `cancel` to cancel."]
            guild = self.client.get_guild(int(m.group(1)))
            if not guild:
                return ["I cannot accept reports of messages from guilds that I'm not in. Please have the guild owner add me to the guild and try again."]
            channel = guild.get_channel(int(m.group(2)))
            if not channel:
                return ["It seems this channel was deleted or never existed. Please try again or say `cancel` to cancel."]
            try:
                message = await channel.fetch_message(int(m.group(3)))
            except discord.errors.NotFound:
                return ["It seems this message was deleted or never existed. Please try again or say `cancel` to cancel."]

            # Here we've found the message - it's up to you to decide what to do next!
            self.state = State.MESSAGE_IDENTIFIED
            return ["I found this message:", "```" + message.author.name + ": " + message.content + "```", \
                    "Please specify why you reported this post:\n" +
                    "Enter `1` for Spam: Repeated, unwanted and/or unsolicited actions, whether automated or manual, that negatively effect platform communities\n" +
                    "Enter `2` for Offensive Content: Material that can be considered vulgar, obscene, or offensive\n" +
                    "Enter `3` for Propaganda against domestic minority groups: Content posted by a political actor containing misleading information about a domestic minority group\n" +
                    "Enter `4` for Imminent Danger: Content that places an individual at serious risk of death or serious physical harm\n" +
                    "Enter `5` for Sexual Content: Content depicting sexual behavior\n" +
                    "Enter `6` for Harassment: Content that aggressively intmidates or pressures someone\n" +
                    "Enter `cancel` to cancel the report"]
        
        if self.state == State.MESSAGE_IDENTIFIED:
            m = message.content
            if (m not in ['1', '2', '3', '4', '5', '6']):
                return ["Please format your response as one of these options:\n" +
                        "Enter `1` for Spam: Repeated, unwanted and/or unsolicited actions, whether automated or manual, that negatively effect platform communities\n" +
                        "Enter `2` for Offensive Content: Material that can be considered vulgar, obscene, or offensive\n" +
                        "Enter `3` for Propaganda against domestic minority groups: Content posted by a political actor containing misleading information about a domestic minority group\n" +
                        "Enter `4` for Imminent Danger: Content that places an individual at serious risk of death or serious physical harm\n" +
                        "Enter `5` for Sexual Content: Content depicting sexual behavior\n" +
                        "Enter `6` for Harassment: Content that aggressively intmidates or pressures someone\n" +
                        "Enter `cancel` to cancel the report"]
            elif (m == '3'):
                self.state = State.AWAITING_GROUP
                return ["Which group does this target?\n" +
                    "Enter `1` for: Religious Group\n" +
                    "Enter `2` for: Political Group\n" +
                    "Enter `3` for: Ethnic/Racial Group\n" +
                    "Enter `4` for: Other\n" +
                    "Enter `cancel` to cancel the report"]
            else:
                self.state = State.REPORT_COMPLETE
                return ["Thank you for filing this report! We will review this post and take the appropriate action"]
        
        if self.state == State.AWAITING_GROUP:
            m = message.content
            if (m not in ['1', '2', '3', '4']):
                return ["Please format your response as one of these options:\n" +
                    "Enter `1` for: Religious Group\n" +
                    "Enter `2` for: Political Group\n" +
                    "Enter `3` for: Ethnic/Racial Group\n" +
                    "Enter `4` for: Other\n" +
                    "Enter `cancel` to cancel the report"]

            self.state = State.ACTION_CHOSEN
            return ["Thank you for filing this report. Would you like to:\n" +
                "Enter `1` for: Block this user\n" +
                "Enter `2` for: Filter our content similar to this post\n" +
                "Enter `3` for: Both of the above\n" +
                "Enter `4` for: None of the above\n" +
                "Enter `cancel` to cancel the report"]
        
        if (self.state == State.ACTION_CHOSEN):
            m = message.content
            if (m not in ['1', '2', '3', '4']):
                return ["Please format your response as one of these options:\n" +
                    "Enter `1` for: Religious Group\n" +
                    "Enter `2` for: Political Group\n" +
                    "Enter `3` for: Ethnic/Racial Group\n" +
                    "Enter `4` for: Other\n" +
                    "Enter `cancel` to cancel the report"]
            
            self.state = State.REPORT_COMPLETE
            return ["Thank you for filing this report! We will review this post and take the appropriate action"]
            
        return []

    def report_complete(self):
        return self.state == State.REPORT_COMPLETE
    


    

