### README for Onyx-Bot

---

## Introduction

Onyx-Bot is a versatile and feature-rich Discord bot designed to enhance user interaction and provide various utilities such as dream journal tracking, statistical analysis, and automated tasks like wake-back-to-bed (WBTB) reminders.

## Features

### 1. Dream Journal
- **adddream**: Adds a new dream entry to the user's journal.
- **deletedream**: Deletes a specific dream entry.
- **listdreams**: Lists all dream entries for a user.
- **searchdreams**: Searches for dream entries containing specific keywords.
- **viewdream**: Views the content of a specific dream entry.
- **dreamcalendar**: Displays a calendar view of dreams.
- **userdreamstats**: Shows detailed dream statistics for a user.
- **generaldreamstats**: Shows general dream statistics for the entire server.

### 2. Profile
- **addrl**: Adds a certain number of lucid dreams to a user's profile.
- **profile**: Displays the user's profile with dream statistics.
- **setrl**: Sets the number of lucid dreams on a user's profile.

### 3. Statistics
- **mystats**: Displays personal message statistics over different time periods.
- **rank**: Displays the ranking of the most active users based on message count.

### 4. Reactions
- **on_message**: Automatically adds reactions to specific keywords or phrases in messages.

### 5. Wake-Back-To-Bed (WBTB)
- **wbtb**: Sets an alarm for WBTB practice.
- **wbtblist**: Lists all set WBTB alarms for users.

### 6. Welcome and Leave Messages
- **welcome**: Sends a welcome message to new members.
- **leave**: Sends a message when a member leaves the server.

## File Structure

- `cogs/`: Contains the different modules (cogs) for the bot's functionalities.
  - `__init__.py`
  - `dreamjournal.py`
  - `dreamjournal2.py`
  - `dreamjournal3.py`
  - `leave.py`
  - `profile.py`
  - `reactions.py`
  - `stats.py`
  - `stats2.py`
  - `stats3.py`
  - `wbtb.py`
  - `welcome.py`
- `data/`: Contains the data files used by the bot.
  - `avatars/`
  - `247353196266127360_calendar.png`
  - `dreams.json`
  - `message_stats.json`
  - `user_data.json`
- `venv/`: Virtual environment for dependencies.
- `bot.py`: Main script to run the bot.

## Setup Instructions

1. Clone the repository: `git clone https://github.com/Alexandre78500/Onyx-Bot.git`
2. Install dependencies: `pip install -r requirements.txt`
3. Configure the bot token and other environment variables in a `.env` file.
4. Run the bot: `python bot.py`

## Contributing

Please read the [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

This README provides a comprehensive overview of Onyx-Bot's features, file structure, setup instructions, and contributing guidelines. For further assistance or questions, feel free to open an issue or contact the project maintainers.