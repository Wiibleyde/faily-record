import discord
from discord import app_commands, ui
from discord.ext import commands, tasks
import datetime
import os
import json
import sqlite3

class Logger:
    def __init__(self, fileName, debugMode=False):
        self.fileName = fileName
        self.debugMode = debugMode

    def info(self, message):
        stringToWrite = f"[INFO] [{datetime.datetime.now()}] {message}"
        print(stringToWrite)
        with open(self.fileName, "a") as file:
            file.write(stringToWrite + "\n")

    def error(self, message):
        stringToWrite = f"[ERROR] [{datetime.datetime.now()}] {message}"
        print(stringToWrite)
        with open(self.fileName, "a") as file:
            file.write(stringToWrite + "\n")

    def warning(self, message):
        stringToWrite = f"[WARN] [{datetime.datetime.now()}] {message}"
        print(stringToWrite)
        with open(self.fileName, "a") as file:
            file.write(stringToWrite + "\n")

    def debug(self, message):
        if not self.debugMode:
            return
        stringToWrite = f"[DEBUG] [{datetime.datetime.now()}] {message}"
        print(stringToWrite)
        with open(self.fileName, "a") as file:
            file.write(stringToWrite + "\n")

class Config:
    def __init__(self, fileName):
        self.fileName = fileName
        if not os.path.exists(self.fileName):
            self.createFile()
            logs.info("Created config file")
            logs.error("Please fill in the config file")
            exit()
        self.config = self.loadFile()
        self.botToken = self.config["BotToken"]
        logs.debug(f"Bot token: {self.botToken}")
        self.fdoChan = self.config["fdoChan"]
        logs.debug(f"FDO channel: {self.fdoChan}")
        self.medicChan = self.config["medicChan"]
        logs.debug(f"Medic channel: {self.medicChan}")
        self.otherChan = self.config["otherChan"]
        logs.debug(f"Other channel: {self.otherChan}")
        self.jugeRoleId = self.config["jugeRoleId"]
        logs.debug(f"Juge role: {self.jugeRoleId}")
        self.adminRoleId = self.config["adminRoleId"]


    def createFile(self):
        with open(self.fileName, "w") as f:
            json.dump({"BotToken": "", "fdoChan":0,"medicChan":0,"otherChan":0,"jugeRoleId":1071406789368741969,"adminRoleId":1071263552675000400}, f, indent=4)

    def loadFile(self):
        with open(self.fileName, "r") as f:
            return json.load(f)
        
    def saveFile(self):
        with open(self.fileName, "w") as f:
            json.dump(self.config, f, indent=4)

    def setKey(self,key,value):
        self.config[key] = value
        self.saveFile()

    def getKey(self,key):
        return self.config[key]

class Data:
    def __init__(self, fileName):
        self.fileName = fileName
        req = "CREATE TABLE IF NOT EXISTS records (id INTEGER PRIMARY KEY, name TEXT, date TEXT, type TEXT, description TEXT, juge TEXT)"
        self.conn = sqlite3.connect(self.fileName)
        self.cursor = self.conn.cursor()
        self.cursor.execute(req)
        self.conn.commit()

    def addRecord(self, name, date, type, description, juge):
        req = "INSERT INTO records (name, date, type, description, juge) VALUES (?, ?, ?, ?, ?)"
        self.cursor.execute(req, (name, date, type, description, juge))
        self.conn.commit()
        logs.debug(f"Added record {name} by {juge}")

    def getRecords(self):
        req = "SELECT * FROM records"
        self.cursor.execute(req)
        return self.cursor.fetchall()
    
    def getRecord(self, id):
        req = "SELECT * FROM records WHERE id = ?"
        self.cursor.execute(req, (id,))
        return self.cursor.fetchone()
    
    def updateRecord(self, id, name, date, type, description, juge):
        req = "UPDATE records SET name = ?, date = ?, type = ?, description = ?, juge = ? WHERE id = ?"
        self.cursor.execute(req, (name, date, type, description, juge, id))
        self.conn.commit()

    def deleteRecord(self, id):
        req = "DELETE FROM records WHERE id = ?"
        self.cursor.execute(req, (id,))
        self.conn.commit()
        logs.debug(f"Deleted record {id}")

    def getRecordByType(self, type):
        req = "SELECT * FROM records WHERE type = ?"
        self.cursor.execute(req, (type,))
        return self.cursor.fetchall()

class Addrecord(ui.Modal, title="Ajouter un record"):
    titleRecord = ui.TextInput(label="Titre du record", placeholder="Titre du record", required=True)
    dateRecord = ui.TextInput(label="Date du record", placeholder="Date du record", required=True)
    typeRecord = ui.TextInput(label="Type du record", placeholder="FDO, Medic, Autre", required=True)
    descriptionRecord = ui.TextInput(label="Description du record", placeholder="Description du record", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        data.addRecord(str(self.titleRecord), str(self.dateRecord), str(self.typeRecord), str(self.descriptionRecord), str(interaction.user.name))
        await interaction.response.send_message("Record ajouté", ephemeral=True)

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

@bot.event
async def on_ready():
    logs.info("Bot is ready")
    try:
        synced = await bot.tree.sync()
        logs.debug(f"Synced {len(synced)} commands")
        logs.debug(f"Commands: {synced}")
    except Exception as e:
        logs.error(f"Failed to sync commands: {e}")

@bot.tree.command(name="addrecord", description="Ajouter un record")
async def addrecord(interaction: discord.Interaction):
    logs.info(f"addrecord command used by {interaction.user}")
    modal = Addrecord()
    await interaction.response.send_modal(modal)
    await modal.wait()
    await interaction.followup.send("Record ajouté")
    if str(modal.typeRecord) == "FDO":
        channel = bot.get_channel(config.fdoChan)
        embed = discord.Embed(title=str(modal.titleRecord), description=str(modal.descriptionRecord), color=0x000fff)
    elif str(modal.typeRecord) == "Medic":
        channel = bot.get_channel(config.medicChan)
        embed = discord.Embed(title=str(modal.titleRecord), description=str(modal.descriptionRecord), color=0xff0000)
    else:
        channel = bot.get_channel(config.otherChan)
        embed = discord.Embed(title=str(modal.titleRecord), description=str(modal.descriptionRecord), color=0x109500)
    embed.set_author(name=str(interaction.user.name))
    embed.set_footer(text=f"ID: {data.getRecords()[-1][0]}")
    await channel.send(embed=embed)
    
if __name__ == '__main__':
    logs = Logger("logs.log", True)
    config = Config("config.json")
    data = Data("data.db")
    logs.info("Starting bot...")
    bot.run(config.botToken, log_level=0, reconnect=True)
