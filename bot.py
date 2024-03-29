from __future__ import annotations
from datetime import datetime
from dotenv.main import load_dotenv
import os
import discord
from discord.ext import commands
from discord.message import Message
from backendService import pingBackend, uploadFight
from readScreenshot import readDofusScreenshot
import cv2

bot = commands.Bot(command_prefix='%', case_insensitive=True)

monitor_channels = []
output_channel = 0


async def processScreenshot(attachment, message:Message):
    # get the ID to use (from backend)
    # TODO: need to save it with the right extension? not always png??
    # https://stackoverflow.com/questions/62375567/how-to-check-for-file-extension-in-discord-py
    formattedDatetime = datetime.strftime(message.created_at, '%Y%m%dT%H%M%SZ')
    tempPath = f'temp/{formattedDatetime}.png'
    tempProcessedPath = f'temp/{formattedDatetime}_processed.png'

    # save screenshot, analyze screenshot, and send info (display typing indicator)
    await attachment.save(tempPath, use_cached=True)
    outputChannel = bot.get_channel(output_channel)
    orignalChannel = message.channel
    async with orignalChannel.typing():
        # read the screenshot and save the processed image
        img, fight = readDofusScreenshot(tempPath)
        cv2.imwrite(tempProcessedPath, img)

        # update the fight object with info from the discord message
        fight.filePath = tempPath # this is needed so backend service knows where the temporary image is located
        fight.guildId = message.guild.id
        fight.channelId = message.channel.id
        fight.date = message.created_at # NOTE: discord message.created_at is in UTC. (dofus time is UTC+2hr)

        fight.id = uploadFight(fight)

        # handle if fight fails to upload
        if fight.id == 0:
            await message.reply('an error occured while attempting to upload this fight to server :( tell chonk to look at the logs i guess')
        else:
            # get formatted embed object from fight object
            (embed, _imgFile) = fight.getEmbed(outputChannel.guild.icon_url, False)

            # attach the processed image and send embed
            imgFile = discord.File(tempProcessedPath, filename='fight.png')
            embed.set_image(url='attachment://fight.png')
            await outputChannel.send(embed=embed, file=imgFile)
            # now that it's sent, delete the temporary processed image
            if os.path.exists(tempProcessedPath):
                os.remove(tempProcessedPath)

            # send some info back to the channel the screenshot came from
            # format winners and losers group:
            winners = ''
            losers = ''
            for p in fight.players:
                deadText = ''
                swordText = ''
                if p.isDead:
                    deadText = '*'
                if p.position.upper() == fight.sword.upper():
                    swordText = ' [A]'
                if (p.position[0].upper() == "W"):
                    winners = winners + f"{p.position[1]}. ({p.characterClass}) {p.characterName}{deadText}{swordText}\n"
                else:
                    losers = losers + f"{p.position[1]}. ({p.characterClass}) {p.characterName}{deadText}{swordText}\n"

            # check to see if there were no losers (could be none if there was no def)
            if losers == '':
                losers = 'None'

            # see if fight has been modified
            modifiedStr = ''
            if fight.modified != 0:
                modifiedStr = '*'

            # format the rest of the embed object
            embed2 = discord.Embed(color=0xf5f2ca)
            embed2.add_field(name='Winners', value=winners, inline=True)
            embed2.add_field(name='Losers', value=losers, inline=True)
            embed2.add_field(name='Names are incorrect?', value=f"To make corrections, try the '%correct' command. (do '%help correct' if you are confused.) (web interface coming soon!)", inline=False)
            # embed2.add_field(name='Duplicate?', value=f"Is this fight a duplicate of XXXXX? If no, please confirm by xxxxx. If yes, please yyyyy.", inline=False)
            embed2.set_author(name=f"ID: {fight.id}{modifiedStr} ({fight.date.strftime('%Y-%m-%d')})", icon_url=outputChannel.guild.icon_url)
            # embed2.set_footer(text=f"* = character is dead.\n[A] = Attacker")
            # await message.reply(embed=embed2, mention_author=False)

            # show on original message that everything is done by reacting with :eye: emoji
            await message.add_reaction(u"\U0001F441")

async def processMessage(message:Message):
    # check to see if message includes a link with an image file extension
    # TODO: handle these properly instead of throwing error
    extensions = ('.png', '.jpg', '.jpeg')
    for ext in extensions:
        if message.content.lower().endswith(ext):
            print('this one was a link with the right ending')
            # imutils.url_to_image(message.content)
            # # img_data = requests.get(message.content).content
            # # img = cv2.imread(img_data)
            # # cv2.imshow('test', img)
            # # cv2.imwrite(f"{formattedDatetime}.png", img)
            # # with open(f'{formattedDatetime}{ext}', 'wb') as handler:
            #     # handler.write(img_data)
            await message.reply("please... just copy and paste the image itself, not the link... chonk hasnt figured this out yet :(")
            return

    for attachment in message.attachments:
        if attachment.filename.lower().endswith(extensions):
            await processScreenshot(attachment, message)

@bot.command()
async def ping(ctx):
    await ctx.send(f'pong! {round(bot.latency * 1000)}ms')
    await ctx.send(f'backend pong? {pingBackend()}ms')
    print(f'pong! {round(bot.latency * 1000)}ms')
    print(f'backend pong! {pingBackend()}ms')

@bot.event
async def on_ready():
    print(f'Bot is Online logged in as {bot.user}')

    # create the directories to save files in later
    # for g in bot.guilds:
    #     for channelId in monitor_channels:
    #         path = f'saved/{g.id}/{channelId}'
    #         if not os.path.exists(path):
    #             os.makedirs(path)
    #             print(f'created path: {path}')

    return await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name='Dofus'))

@bot.event
async def on_message(message:Message):
    # ignore message if it comes from this bot
    if message.author.id == bot.user.id:
        return
    
    # look at messages in monitored channels
    if message.channel.id in monitor_channels:
        await processMessage(message)

    # process all other commands
    await bot.process_commands(message)

def main():
    # read variables from .env file
    load_dotenv()

    # store which channels .env tells us to monitor and which is output
    # TODO: this should be some sort of config JSON file or something, and channels should not be 'hardcoded' into .env file
    monitor_channels.append(int(os.environ['MONITOR1']))
    monitor_channels.append(int(os.environ['MONITOR2']))
    monitor_channels.append(int(os.environ['MONITOR3']))
    # TODO: need to call it a global variable to change it gobally... by why didnt i need to do it like that for monitor_channels list?? i need to learn more wtf
    global output_channel
    output_channel = int(os.environ['OUTPUT_CHANNEL'])
    print(f'output channel: {output_channel}')
    print(f'monitored channels: {monitor_channels}')

    # get the discord bot token and start bot
    token = os.environ['DISCORD_TOKEN']
    bot.run(token)

if __name__ == '__main__':
    main()