import discord
from discord import app_commands, ui
from discord.ext import commands, tasks
import datetime
import os
import json
import sqlite3
import requests
from bs4 import BeautifulSoup

class Logger:
    def __init__(self, fileName, debugMode=False):
        self.fileName = fileName
        self.debugMode = debugMode
        if debugMode:
            self.debug("Debug mode enabled")
        else:
            self.info("Debug mode disabled")

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
        stringToWrite = f"[DEBUG] [{datetime.datetime.now()}] {message}"
        if self.debugMode:
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
        req1 = "CREATE TABLE IF NOT EXISTS records (id INTEGER PRIMARY KEY, name TEXT, date TEXT, type TEXT, description TEXT, juge TEXT)"
        req2 = "CREATE TABLE IF NOT EXISTS message (id INTEGER PRIMARY KEY, idMessage INTEGER, idRecord INTEGER)"
        self.conn = sqlite3.connect(self.fileName)
        self.cursor = self.conn.cursor()
        self.cursor.execute(req1)
        self.cursor.execute(req2)
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
    
    def getRandomRecord(self):
        req = "SELECT * FROM records ORDER BY RANDOM() LIMIT 1"
        self.cursor.execute(req)
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
    
    def addMessage(self, idMessage, idRecord):
        req = "INSERT INTO message (idMessage, idRecord) VALUES (?, ?)"
        self.cursor.execute(req, (idMessage, idRecord))
        self.conn.commit()
        logs.debug(f"Added message {idMessage} for record {idRecord}")

    def getMessage(self, recordId):
        req = "SELECT * FROM message WHERE idRecord = ?"
        self.cursor.execute(req, (recordId,))
        return self.cursor.fetchone()
    
    def deleteMessage(self, recordId):
        req = "DELETE FROM message WHERE idRecord = ?"
        self.cursor.execute(req, (recordId,))
        self.conn.commit()
        logs.debug(f"Deleted message {recordId}")

class Addrecord(ui.Modal, title="Ajouter un record"):
    titleRecord = ui.TextInput(label="Titre du record", placeholder="Titre du record", required=True)
    dateRecord = ui.TextInput(label="Date du record", placeholder="Date du record", required=True)
    typeRecord = ui.TextInput(label="Type du record", placeholder="FDO, Medic, Autre", required=True)
    descriptionRecord = ui.TextInput(label="Description du record", placeholder="Description du record", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        data.addRecord(str(self.titleRecord), str(self.dateRecord), str(self.typeRecord), str(self.descriptionRecord), str(interaction.user.name))
        await interaction.response.send_message("Record ajouté", ephemeral=True)

def getArgs():
    args = os.sys.argv
    if len(args) > 1:
        if args[1] == "--debug":
            return True
    else:
        return False
    
def getWikiPage(search):
    url = "https://failyv.fandom.com/fr/wiki/Spécial:Recherche?query=+"+search.replace(" ","+")
    response = requests.request("GET", url)
    data=response.text
    soup = BeautifulSoup(data, 'html.parser')
    for link in soup.find_all('a'):
        if link.get('class') != None:
            if link.get('class')[0] == "unified-search__result__link":
                return link.get('href')
    return None

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
logs = Logger("logs.log", getArgs())
config = Config("config.json")
data = Data("data.db")

@bot.event
async def on_ready():
    logs.info("Bot is ready")
    try:
        StatusLoop.start()
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
    messaage = await channel.send(embed=embed)
    messageId = messaage.id
    recordId = data.getRecords()[-1][0]
    data.addMessage(messageId, recordId)

@bot.tree.command(name="removerecord", description="Supprimer un record")
async def removerecord(interaction: discord.Interaction, id: int):
    logs.info(f"removerecord command used by {interaction.user}")
    try:
        messageData = data.getMessage(id)
        if messageData is not None:
            logs.debug(f"Deleting message {messageData[1]}")
            if str(data.getRecord(id)[3]) == "FDO":
                channel = bot.get_channel(config.fdoChan)
            elif str(data.getRecord(id)[3]) == "Medic":
                channel = bot.get_channel(config.medicChan)
            else:
                channel = bot.get_channel(config.otherChan)
            message = await channel.fetch_message(messageData[1])
            logs.debug(message)
            await message.delete()
            data.deleteMessage(id)
            data.deleteRecord(id)
        await interaction.response.send_message("Record supprimé", ephemeral=True)
    except discord.NotFound:
        await interaction.response.send_message("Le message correspondant à cet ID est introuvable", ephemeral=True)
    except Exception as e:
        logs.error(f"Error in removerecord command: {e}")
        await interaction.response.send_message("Une erreur s'est produite lors de la suppression du record", ephemeral=True)

@bot.tree.command(name="record", description="Afficher un record")
async def record(interaction: discord.Interaction, id: int):
    logs.info(f"record command used by {interaction.user}")
    record = data.getRecord(id)
    if record is not None:
        embed = discord.Embed(title=record[1], description=record[3], color=0x000fff)
        embed.set_author(name=record[4])
        embed.set_footer(text=f"ID: {record[0]}")
        await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        await interaction.response.send_message("Record introuvable", ephemeral=True)

@bot.tree.command(name="setchannel", description="Définir un channel")
async def setchannel(interaction: discord.Interaction, channel: int, type: str):
    logs.info(f"setchannel command used by {interaction.user}")
    if type == "FDO":
        config.setKey("fdoChan", int(channel))
    elif type == "Medic":
        config.setKey("medicChan", int(channel))
    elif type == "Autre":
        config.setKey("otherChan", int(channel))
    else:
        await interaction.response.send_message("Type de channel invalide", ephemeral=True)
        return
    await interaction.response.send_message("Channel défini", ephemeral=True)


# @bot.tree.command(name="editrecord", description="Modifier un record")
# async def editrecord(interaction: discord.Interaction, id: int, title: str, date: str, description: str):
#     logs.info(f"editrecord command used by {interaction.user}")
#     try:
#         messageId = data.getMessage(id)[1]
#         if messageId is not None:
#             logs.debug(f"Editing message {messageId}")
#             channel = bot.get_channel(config.fdoChan)
#             messageId = await channel.fetch_message(messageId)
#             await messageId.edit(embed=discord.Embed(title=title, description=description, color=0x000fff))
#             data.editRecord(id, title, date, description)
#         await interaction.response.send_message("Record modifié", ephemeral=True)
#     except discord.NotFound:
#         await interaction.response.send_message("Le message correspondant à cet ID est introuvable", ephemeral=True)
#     except Exception as e:
#         logs.error(f"Error in editrecord command: {e}")
#         await interaction.response.send_message("Une erreur s'est produite lors de la modification du record", ephemeral=True)

@bot.tree.command(name="wiki", description="Affiche la page wiki")
async def wiki(interaction: discord.Interaction, search: str, afficher: bool = False):
    logs.info(f"wiki command used by {interaction.user}")
    embed = discord.Embed(title="Wiki", description=f"Résultat de la recherche {search}", color=0x00ff00)
    result = getWikiPage(search)
    if result == None:
        embed.add_field(name="Résultat", value="Aucun résultat", inline=False)
    else:
        embed.add_field(name="Résultat", value=result, inline=False)
    if afficher:
        await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message(embed=embed, ephemeral=True)

@tasks.loop(seconds=60)
async def StatusLoop():
    logs.debug("Updating status")
    try:
        randomRecord = data.getRandomRecord()
        if randomRecord is not None:
            strStatus = f"{randomRecord[1]} - {(randomRecord[4])[0:10]}"
            await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=strStatus))
    except Exception as e:
        logs.error(f"Error in StatusLoop: {e}")
        
if __name__ == '__main__':
    logs.info("Starting bot...")
    bot.run(config.botToken, log_level=0, reconnect=True)
