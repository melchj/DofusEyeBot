from __future__ import annotations
from datetime import datetime
from dataclasses import dataclass
import discord

# TODO: need some validation here for the strings below, so they can't just be random characters?
@dataclass
class Player:
    position:str # 'W1', 'W2', ... , 'L1', 'L2', ...
    characterName:str # 'lucent', 'chonk', 'alaxel', etc...
    characterClass:str
    isDead:int # 0=alive

class Fight:
    id:int
    modified:int
    guildId:int
    channelId:int
    date:datetime
    filePath:str
    sword:str
    players:list[Player]

    def __init__(self, id:int, modified:int, guildId:int, channelId:int, date:datetime, filePath:str, sword:str, players:list[Player]):
        self.id = id
        self.modified = modified
        self.guildId = guildId
        self.channelId = channelId
        self.date = date
        self.filePath = filePath
        self.sword = sword
        self.players = players
    
    def getEmbed(self, iconUrl:str, attachImage:bool=False):
        """
        creates a discord embed object ready to send to a discord channel.
        returns tuple of (embed, imageFile)
        imageFile = None if attackImage==False
        """
        # format winners and losers group:
        winners = ''
        losers = ''
        for p in self.players:
            deadText = ''
            swordText = ''
            if p.isDead:
                deadText = '*'
            if p.position.upper() == self.sword.upper():
                swordText = ' [A]'
            if (p.position[0].upper() == "W"):
                winners = winners + f"{p.position[1]}. ({p.characterClass}) {p.characterName}{deadText}{swordText}\n"
            else:
                losers = losers + f"{p.position[1]}. ({p.characterClass}) {p.characterName}{deadText}{swordText}\n"
        
        # check to see if there were no losers (could be none if there was no def)
        if losers == '':
            losers = 'None'

        modifiedStr = ''
        if self.modified != 0:
            modifiedStr = '*'

        # format the rest of the embed object
        embed = discord.Embed(color=0xf5f2ca)
        embed.add_field(name='Winners', value=winners, inline=True)
        embed.add_field(name='Losers', value=losers, inline=True)
        embed.set_author(name=f"ID: {self.id}{modifiedStr} ({self.date.strftime('%Y-%m-%d')})", icon_url=iconUrl)
        embed.set_footer(text=f"* = character is dead.\n[A] = Attacker")

        imgFile = None
        if attachImage:
            # prep the image to send
            imgFile = discord.File(self.filePath, filename='fight.png')
            embed.set_image(url='attachment://fight.png')

        return (embed, imgFile)

    def toDict(self):
        '''
        returns the fight object as a dictionary object, useful to jsonify then send to backend.
        '''
        resp = {}
        resp['fight_id'] = self.id
        resp['modified'] = self.modified
        resp['guild_id'] = self.guildId
        resp['channel_id'] = self.channelId
        resp['date'] = self.date.timestamp()
        resp['file_path'] = self.filePath
        resp['sword'] = self.sword

        # loop thru all player positions
        positions = ['w1', 'w2', 'w3', 'w4', 'w5', 'l1', 'l2', 'l3', 'l4', 'l5']
        for pos in positions:
            positionFilled = False
            # loop thru list of players to see if any are in this position
            for p in self.players:
                # if there is a player in this position, add stuff to the response object
                if p.position.lower() == pos:
                    positionFilled = True
                    resp[f"{pos}_name"] = p.characterName
                    resp[f"{pos}_class"] = p.characterClass
                    resp[f"{pos}_dead"] = p.isDead
                    break
            # if no player is in this position, fill with default values
            if not positionFilled:
                resp[f"{pos}_name"] = ""
                resp[f"{pos}_class"] = ""
                resp[f"{pos}_dead"] = 0
        
        return resp
