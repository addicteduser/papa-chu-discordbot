import os
import re

import disnake
from disnake.ext import commands
from dotenv import load_dotenv
from disnake.ui import TextInput, Modal
from disnake import TextInputStyle

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
    testguilds=[679218449024811067],
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
    tag_others: bool = commands.Param(
        description="Tag/mention those in your confession (default: True)", default=True
    ),
):
    """Submit a confession to Papa Chu"""
    mentions = get_mentions(confession)

    bot_reply = ""
    if tag_others and mentions:
        bot_reply = bot_reply + f"(cc {mentions})\n\n"

    bot_reply = bot_reply + f"{inter.author.mention} confesses:"
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


@bot.slash_command()
async def long_confess(inter: disnake.ApplicationCommandInteraction):
    """Submit a long confession to Papa Chu (can't tag/mention others using this way)"""

    # Build UI
    components = [
        TextInput(
            label="Confession",
            placeholder="Come, child. Tell me your confession...",
            custom_id="confession",
            style=TextInputStyle.paragraph,
        ),
        TextInput(
            label="Attachment",
            placeholder="Link to image/GIF you want to attach to your confession",
            custom_id="attachment",
            style=TextInputStyle.short,
            required=False,
        ),
    ]

    modal = Modal(
        title="Papa Chu's Confessional",
        custom_id="long_confession",
        components=components,
        timeout=10,
    )
    await inter.response.send_modal(modal=modal)


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
def get_channel_file():
    if os.path.exists("test_channel.txt"):
        return "test_channel.txt"
    else:
        return "channel.txt"


def get_channel_id():
    try:
        with open(get_channel_file(), "r") as f:
            channel_id = int(f.read())
    except:
        channel_id = None
    finally:
        return channel_id


def set_channel_id(channel_id):
    with open(get_channel_file(), "w") as f:
        f.write(str(channel_id))


def get_and_update_confessor_number():
    confessor_number = 0
    if os.path.exists("test_confessor_number.txt"):
        confessor_number_file = "test_confessor_number.txt"
    else:
        confessor_number_file = "confessor_number.txt"

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

    embed.set_footer(
        text="If this confession goes against any of the server's rules of conduct, "
        + "kindly report it to any of the server admins",
        icon_url="https://cdn.discordapp.com/attachments/690444258393587763/1016325498239995915/203c-16px.png",
    )
    if image:
        embed.set_image(url=image)

    return embed


def get_mentions(confession):
    # <@!xxxxx> for pc
    # <!xxxxx> for mobile
    pattern = r"<@!?\d*>"
    mentions = re.findall(pattern, confession)
    return " ".join(mentions)


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


@bot.event
async def on_modal_submit(inter: disnake.ModalInteraction):
    if "long_confession" == inter.custom_id:
        # Set parameters like in /confess
        confession = inter.text_values.get("confession")
        attachment = inter.text_values.get("attachment")

        # /confess code without tag_others
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


#############
## TESTING ##
#############
# @bot.slash_command(guild_ids=[679218449024811067])
# async def confess_test(
#     inter: disnake.CommandInteraction,
# ):


#######################
## DISCORD BOT START ##
#######################
if __name__ == "__main__":
    token = os.getenv("PAPA_CHU_DISCORD_TOKEN")
    bot.run(token)
