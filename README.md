# Onyx Bot

Onyx Bot is a Discord bot designed to help users manage and analyze their dreams, with a particular focus on lucid dreams.

## Features

- **Dream Journal**: Add, list, view, and delete your dreams.
- **Dream Statistics**: Get detailed statistics on your dreams and those of the community.
- **Dream Calendar**: View your dreams on a monthly calendar.
- **Dream Profile**: Manage your dreamer profile, including the number of lucid dreams.
- **WBTB Alarm**: Set alarms for the Wake Back To Bed technique.
- **Activity Statistics**: Track your activity on the server.
- **Idea System**: Submit and review ideas to improve the bot.

## Main Commands

- `o!interactivedream`: Interactive interface to manage your dreams.
- `o!dreamcalendar`: Displays a calendar of your dreams.
- `o!dstats [@member]`: Displays a user's dream statistics.
- `o!gstats`: Displays global dream statistics on the server.
- `o!profile [@member]`: Displays a user's dream profile.
- `o!wbtb <time>`: Sets a WBTB alarm.
- `o!mystats`: Displays your activity statistics on the server.
- `o!submitidea <idea>`: Submits an idea to improve the bot.

## Project Structure

```
onyx-bot/
│
├── bot.py
├── config.py
├── requirements.txt
│
├── cogs/
│   ├── dreamjournal.py
│   ├── profile.py
│   ├── statistics.py
│   ├── utilities.py
│   ├── admin.py
│   ├── fun.py
│   └── help.py
│
├── utils/
│   ├── json_manager.py
│   └── time_utils.py
│
└── data/
    ├── dreams.json
    ├── user_data.json
    └── stats.json
```

## Installation

1. Clone this repository
2. Install the dependencies: `pip install -r requirements.txt`
3. Configure your Discord token in a `.env` file
4. Start the bot: `python bot.py`

## Contribution

Contributions are welcome! Feel free to open an issue or submit a pull request.

## License

This project is licensed under the MIT License.