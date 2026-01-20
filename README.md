# Daily Quote bot for Discord

A simple Discord bot that fetches quotes from a channel and posts them randomly in another channel.

## Description

This bot listens for commands in a Discord server and sends random quotes that have been previously recorded in a channel.  
Commands include:

- `/quote` → fetch a random quote from a source channel into the target channel
- `/id` → get the channel ID
- `/source` → set source channel
- `/target` → set target channel
- `/info` → view current source- and target-channel
- `/total_quotes` → view the total amount of formatted quotes in set target channel

### Dependencies

* Python 3.10+
* discord.py
* python-dotenv

### Installing

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/your-repo.git
   ```

2. Create a .env file in the root folder:
    ```
    DISCORD_TOKEN="token"
    ```

3. Install dependencies

### Executing program

Open the terminal and enter:
    ```
    bot.py
    ```

### Author

Shive

### Note

Bot is still under development.
Thank you for the one-liners, cheese eater Ruud

