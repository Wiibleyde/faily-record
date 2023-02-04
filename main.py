import discord
import sqlite3
import json
import time
import datetime

commandList = ["addrecord", "deleterecord", "editrecord","maintenance","help"]

class Config:
    def __init__(self, fileName):
        self.fileName = fileName
        if not self.isConfig():
            print("Config file not found, creating one...")
            self.createConfig()
        
    def isConfig(self):
        try:
            with open(self.fileName, "r") as f:
                return True
        except FileNotFoundError:
            return False

    def createConfig(self):
        with open(self.fileName, "w") as f:
            json.dump({"token": "your token here", "prefix": "your prefix here", "maintenance": False, "modRoleId": "your mod role id here", "jugeRoleId": "your juge role id here", "fdoChannelId": "your fdo channel id here", "medicChannelId": "your medic channel id here"}, f)

    def loadConfig(self):
        with open(self.fileName, "r") as f:
            return json.load(f)

class Database:
    def __init__(self, fileName):
        self.fileName = fileName
        if not self.isDatabase():
            print("Database file not found, creating one...")
            self.createDatabase()
        self.conn = sqlite3.connect(self.fileName)
        self.cursor = self.conn.cursor()

    def isDatabase(self):
        try:
            with open(self.fileName, "r") as f:
                return True
        except FileNotFoundError:
            return False

    def createDatabase(self):
        with open(self.fileName, "w") as f:
            pass

    def createTable(self):
        self.cursor.execute("CREATE TABLE IF NOT EXISTS logs (id INTEGER PRIMARY KEY, channel_id INTEGER, command TEXT, user_id INTEGER, time TEXT)")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS records(id INTEGER PRIMARY KEY, title TEXT, description TEXT, clip TEXT, image TEXT, user_id INTEGER, time TEXT)")
        self.conn.commit()

    def insertLog(self, channel_id, command, user_id, time):
        self.cursor.execute("INSERT INTO logs VALUES (NULL, ?, ?, ?, ?)", (channel_id, command, user_id, time))
        self.conn.commit()

    def insertRecord(self, title, description, clip, image, user_id, time):
        self.cursor.execute("INSERT INTO records VALUES (NULL, ?, ?, ?, ?, ?, ?)", (title, description, clip, image, user_id, time))
        self.conn.commit()

client = discord.Client()

@client.event
async def on_ready():
    print("Logged in as {0.user}".format(client))

@client.event
async def on_message(message):
    try:
        if message.content.startswith(getPrefix()):
            command = message.content[1:].split(" ")[0]
            if getMaintenance() and not userHasRole(message.author, getModRoleId()):
                embed = discord.Embed(title="Maintenance", description="Le bot est en maintenance.", color=0xff0000)
                await message.channel.send(embed=embed)
                return
            if getMaintenance() and userHasRole(message.author, getModRoleId()):
                await message.channel.send("Le bot est en maintenance mais vous avez les droits de modération.")
            if command == "addrecord" and userHasRole(message.author, getJugeRoleId()):
                # addrecord "<title>" "<description>" "<clip (optional)>"
                args = message.content[1:].split('"')
                if len(args) < 3:
                    embed = discord.Embed(title="Erreur", description="Il manque des arguments.", color=0xff0000)
                    await message.channel.send(embed=embed)
                    return
                title = args[1]
                description = args[3]
                clip = args[5] if len(args) > 5 else None
                db.insertRecord(title, description, clip, None, message.author.id, datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    except Exception as e:
        embed = discord.Embed(title="Erreur", description="Une erreur est survenue.", color=0xff0000)
        embed.add_field(name="Erreur", value=e)
        await message.channel.send(embed=embed)
                
def userHasRole(user, role):
    for r in user.roles:
        if r.id == role:
            return True
    return False

def getToken():
    return config["token"]

def getPrefix():
    return config["prefix"]

def getMaintenance():
    return config["maintenance"]

def getModRoleId():
    return config["modRoleId"]

def getJugeRoleId():
    return config["jugeRoleId"]

def getFdoChannelId():
    return config["fdoChannelId"]

def getMedicChannelId():
    return config["medicChannelId"]

if __name__=='__main__':
    global config
    print("Starting...")
    configFile = Config("conf.json")
    config=configFile.loadConfig()
    print("Loaded config")
    db = Database("database.db")
    db.createTable()
    print("Loaded database")
    print("Starting bot...")
    client.run(getToken())
    print("Bot stopped")
