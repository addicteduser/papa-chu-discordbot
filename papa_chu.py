from unicodedata import name
import disnake
from dotenv import load_dotenv
from disnake.ext import commands
import os

# Load environment variables
load_dotenv()

command_prefix = commands.when_mentioned
description = "A bot to tell your confessions..."
intents = disnake.Intents.default()
bot = commands.Bot(
    case_insensitive=True,
    command_prefix=command_prefix,
    description=description,
    help_command=None,
    intents=intents,
)

#####################
## CONFESS COMMAND ##
#####################
@bot.slash_command()
async def confess(
    inter: disnake.CommandInteraction,
    confession: str = commands.Param(description="Your confession"),
    attachment: str = commands.Param(
        description="Link to image/GIF you want to attach to your confession",
        default=None,
    ),
):
    """Submit a confession to Papa Chu"""
    bot_reply = f"{inter.author.mention} confesses:"
    embed = embed_builder(confession, attachment)

    channel_id = get_channel_id()
    if channel_id:
        channel = bot.get_channel(channel_id)
        await channel.send(bot_reply, embed=embed)
        await inter.send(f"Confession sent in <#{channel_id}>!", ephemeral=True)
    else:
        await inter.send(
            "Use `/set_channel` to configure which channel to send the confessions to"
        )


@bot.slash_command(default_member_permissions=disnake.Permissions(manage_guild=True))
async def set_channel(
    inter: disnake.CommandInteraction,
    channel: disnake.TextChannel = commands.Param(
        description="The channel you want to send the confessions to"
    ),
):
    """Sets which channel to send the confessions"""
    set_channel_id(channel.id)
    await inter.send(f"Confessions will be sent to <#{channel.id}>!")


############
## HELPER ##
############
channel_file = "channel.txt"


def get_channel_id():
    # channel_id = None

    try:
        with open(channel_file, "r") as f:
            channel_id = int(f.read())
    except:
        channel_id = None
    finally:
        return channel_id


def set_channel_id(channel_id):
    with open(channel_file, "w") as f:
        f.write(str(channel_id))


def get_and_update_confessor_number():
    confessor_number_file = "confessor_number.txt"
    confessor_number = 0

    # Get confessor number
    with open(confessor_number_file, "r") as f:
        confessor_number = int(f.read())

    # Update confessor number
    with open(confessor_number_file, "w") as f:
        f.write(str(confessor_number + 1))

    return confessor_number


def embed_builder(description, image=None):
    confessor_number = get_and_update_confessor_number()
    embed = disnake.Embed(
        title=f"Anonymous Confession (#{confessor_number})",
        description=description,
        color=0x1ABC9C,
    )
    if image:
        embed.set_image(url=image)

    return embed


########################
## DISCORD BOT EVENTS ##
########################
@bot.event
async def on_connect():
    print(f"{bot.user.name} has connected to Discord!")
    await bot.change_presence(
        activity=disnake.Activity(
            name="your confessions... | /confess",
            type=disnake.ActivityType.listening,
        )
    )


@bot.event
async def on_ready():
    print(f"{bot.user.name} is live!")


#######################
## DISCORD BOT START ##
#######################
if __name__ == "__main__":
    token = os.getenv("PAPA_CHU_DISCORD_TOKEN")
    bot.run(token)
