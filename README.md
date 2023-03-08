# faily-record

![Last Commit](https://img.shields.io/github/last-commit/wiibleyde/faily-record.svg)
![Build Status](https://travis-ci.org/wiibleyde/faily-record.svg?branch=master)

A simple discord bot to record your fails and share them with your friends. (Made for the discord [Faily Guinness Record](https://discord.gg/YtGRQs9KHf) server)

## Installation

### Requirements

- Python 3.10
- Discord.py 2.*
- A discord bot token

### Setup

1. Clone the repository
2. Start the bot with `python3 main.py`
3. Complete the `config.json` file
4. Restart the bot

## Usage

### Commands

- `/addrecord` - Add a new record (This will open a discord form to add the record) with an unique id
- `/removerecord` - Remove a record with the given id

### Configuration

The `config.json` file contains the following options:

- `BotToken` - The discord bot token
- `fdoChan` - The channel id where the FDO records are posted
- `medicChan` - The channel id where the medics records are posted
- `otherChan` - The channel id where the other records are posted
- `jugeRoleId` - The role id of the juge (The one who can add and remove records)
- `adminRoleId` - The role id of the admin (The one who can add and remove records and other stuff in the future)

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## Authors

- [Wiibleyde](https://www.github.com/wiibleyde)


