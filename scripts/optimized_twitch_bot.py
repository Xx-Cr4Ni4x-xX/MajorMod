from twitchio.ext import commands
import openai
import json
import os
import requests

# Load API keys and tokens from auth_config.json file
AUTH_FILE = os.path.join(os.path.dirname(__file__), '..', 'auth', 'auth_config.json')
try:
    with open(AUTH_FILE, 'r') as file:
        auth_config = json.load(file)
except FileNotFoundError:
    print("Error: Authentication config file not found.")
    auth_config = {}

# Extract tokens and keys from the loaded config
TWITCH_TOKEN = auth_config.get('TWITCH_TOKEN', 'default_twitch_token')
TWITCH_CLIENT_ID = auth_config.get('TWITCH_CLIENT_ID', 'default_twitch_client_id')
BOT_NICK = auth_config.get('BOT_NICK', 'default_bot_name')
CHANNEL = auth_config.get('CHANNEL', 'default_channel_name')
OPENAI_API_KEY = auth_config.get('OPENAI_API_KEY', 'default_openai_api_key')
openai.api_key = OPENAI_API_KEY

# Configuration file path for bot settings
CONFIG_FILE = os.path.join(os.path.dirname(__file__), '..', 'config', 'config.json')

# Default configuration settings
DEFAULT_CONFIG = {
    'chat_rules': [
        "Be respectful.",
        "No hate speech, harassment, or discrimination.",
        "No spamming or inappropriate content."
    ],
    'warnings_before_ban': 3,
    'ignore_broadcaster': False,
    'ignore_mods': False
}

# Load or initialize configuration
def load_config():
    try:
        with open(CONFIG_FILE, 'r') as config_file:
            return json.load(config_file)
    except (FileNotFoundError, json.JSONDecodeError):
        return DEFAULT_CONFIG

# Global configuration variable
current_config = load_config()

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(token=TWITCH_TOKEN, prefix='!', initial_channels=[CHANNEL])
        self.streamer = CHANNEL.lower()
        self.moderators = []

    async def event_ready(self):
        print(f'Logged in as | {self.nick}')
        print(f'Connected to channel | {CHANNEL}')
        await self.update_moderators_list()

    async def event_message(self, message):
        print(f'Message received from {message.author.name}: {message.content}')

        # Skip if the message is from the bot itself
        if message.author.name.lower() == BOT_NICK.lower():
            return

        # Check for ignore conditions based on configuration
        if current_config['ignore_broadcaster'] and message.author.name.lower() == self.streamer:
            print("Ignoring broadcaster message")
            return
        if current_config['ignore_mods'] and message.author.is_mod:
            print("Ignoring moderator message")
            return

        # Debug statement to confirm command processing
        print("Command processing started")

        # Process commands using handle_commands
        await self.handle_commands(message)

    async def update_moderators_list(self):
        # Fetch moderators using Twitch API
        broadcaster_id = self.get_broadcaster_id()
        if broadcaster_id:
            url = f'https://api.twitch.tv/helix/moderation/moderators?broadcaster_id={broadcaster_id}'
            headers = {
                'Client-ID': TWITCH_CLIENT_ID,
                'Authorization': f'Bearer {TWITCH_TOKEN}'
            }
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                self.moderators = [moderator['user_name'].lower() for moderator in data['data']]
                print(f"Moderators list updated: {self.moderators}")
            else:
                print(f"Failed to fetch moderators: {response.status_code} - {response.json()}")
        else:
            print("Failed to fetch broadcaster ID. Please check your Client ID and Token.")

    @staticmethod
    def get_broadcaster_id():
        # Fetch broadcaster (streamer) ID using Twitch API
        url = f'https://api.twitch.tv/helix/users?login={CHANNEL}'
        headers = {
            'Client-ID': TWITCH_CLIENT_ID,
            'Authorization': f'Bearer {TWITCH_TOKEN}'
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return data['data'][0]['id']
        else:
            print(f"Failed to fetch broadcaster ID: {response.status_code} - {response.json()}")
            return None

    @commands.command(name='hello')
    async def hello(self, ctx):
        # Debug statement to confirm command is executed
        print(f"Executing hello command for {ctx.author.name}")
        await ctx.send(f'Hello, {ctx.author.name}! The bot is working!')

    @commands.command(name='ping')
    async def ping_command(self, ctx):
        # Debug statement to confirm command is executed
        print(f"Executing ping command for {ctx.author.name}")
        await ctx.send(f'Pong! Hello, {ctx.author.name}!')

    @commands.command(name='ai_test')
    async def ai_test(self, ctx):
        # Debug statement to confirm command is executed
        print(f"Executing AI test command for {ctx.author.name}")
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Say hello to the user."}
                ]
            )
            await ctx.send(f'AI says: {response["choices"][0]["message"]["content"].strip()}')
        except Exception as e:
            await ctx.send(f'Failed to connect to OpenAI: {str(e)}')


if __name__ == '__main__':
    bot = Bot()
    bot.run()
