import asyncio
import datetime
import random

import discord
import requests
import json
from textwrap import TextWrapper

from bot import global_vars
from bot import aerialace_data_manager
from bot import aerialace_cache_manager


class PokeData:

    p_id = 0
    p_name = ""
    p_types = ""
    p_region = ""
    p_abilities = ""
    p_weight = 0.0
    p_height = 0.0
    image_link = ""
    p_info = ""
    p_stats = {}
    p_total_stats = 0
    p_evolution_chain = ""
    p_rarity = ""

# starts the rich presence cycle
async def start_rich_presence_cycle(client, repeat_time):
    await set_rich_presence(client)
    while True:
        await asyncio.sleep(repeat_time)
        await set_rich_presence(client)

# set rich presence
async def set_rich_presence(client):
    rand = random.randint(1, 3)
    status = discord.Status.online
    if rand == 1:
        playing_game = discord.Game(name="Dev's shitty games")
        await client.change_presence(activity=playing_game, status=status)
    elif rand == 2:
        watching_prefix = discord.Activity(name="prefix: -aa", type=3)
        await client.change_presence(activity=watching_prefix, status=status)
    else:
        listening_prefix = discord.Activity(name="-aa help", type=2)
        await client.change_presence(activity=listening_prefix, status=status)

# for getting the help embed
def get_help_embed():
    embd = discord.Embed(color=global_vars.NORMAL_COLOR)
    embd.title = "Aerial Ace Help"

    # help fields
    embd.add_field(
        name="Random Pokemon", 
        value="`-aa rp` or `-aa rand_poke`", 
        inline=False
    )
    embd.add_field(
        name="View Dex Entry",
        value="`-aa dex <pokedex id>` or `-aa dex <pokemon name>`",
        inline=False
    )
    embd.add_field(
        name="Rolling", 
        value="`-aa roll` or `-aa roll <upper limit>`", 
        inline=False
    )
    embd.add_field(
        name="Set Favourite Pokemon",
        value="`-aa set_fav <pokemon name>` or `-aa sf <pokemon name>`",
        inline=False
    )
    embd.add_field(
        name="View Favourite Pokemon", 
        value="`-aa fav`", 
        inline=False
    )
    embd.add_field(
        name="Stats Check",
        value="`-aa stats <pokemon>`", 
        inline=False)
    embd.add_field(
        name="Moveset Check",
        value="`-aa moveset <pokemon name>` or `-aa ms <pokemon name>`",
        inline=False,
    )
    embd.add_field(
        name="Tierlists",
        value="`-aa tierlist <tier type>` or `-aa tl <tier type>`",
        inline=False
    )
    embd.add_field(
        name="Add yourself to a tag",
        value="`-aa tag <tag>`",
        inline=False
    )
    embd.add_field(
        name="Ping users assigned to a tag",
        value="`-aa tag_ping <tag>` or `-aa tp <tag>`",
        inline=False
    )
    embd.add_field(
        name="See users assigned to a tag",
        value="`-aa tag_show <tag>` or `-aa ts <tag>`",
        inline=False
    )
    embd.add_field(
        name="Log Battles",
        value="`-aa log_battle @winner @loser` or `-aa lb @winner @loser`",
        inline=False
    )
    embd.add_field(
        name="See battle score",
        value="`-aa battle_score` or `-aa bs`",
        inline=False
    )
    embd.add_field(
        name="See Battle leaderboard of the server",
        value="`-aa battle_lb` or `-aa blb`",
        inline=False
    )

    embd.set_thumbnail(url=global_vars.AVATAR_LINK)
    embd.set_footer(text="Invite using -aa invite")

    return embd

# for getting a pokemon of desired index
async def get_poke_by_id(poke_id):

    if poke_id == "":
        return None

    if poke_id == "":
        return None

    poke = PokeData()

    general_link = "https://pokeapi.co/api/v2/pokemon/{0}".format(poke_id)
    general_response = requests.get(general_link)
    general_data = json.loads(general_response.text)

    species_link = general_data["species"]["url"]
    species_response = requests.get(species_link)
    species_data = json.loads(species_response.text)

    generation_response = requests.get("https://pokeapi.co/api/v2/generation/{name}/".format(name=species_data["generation"]["name"]))
    generation_data = json.loads(generation_response.text)

    evolution_response = requests.get(species_data["evolution_chain"]["url"])
    evolution_data = json.loads(evolution_response.text)

    poke.p_id = general_data["id"]

    # get name
    poke.p_name = general_data["name"].capitalize()

    # get height and weight
    poke.p_height = float(general_data["height"]) / 10
    poke.p_weight = float(general_data["weight"]) / 10

    # get types
    types = general_data["types"]
    for i in range(0, len(types)):
        poke.p_types += types[i]["type"]["name"].capitalize()

        if i != len(types) - 1:
            poke.p_types += "\n"

    # get_region
    poke.p_region = generation_data["main_region"]["name"].capitalize()

    # get abilities
    abilities = general_data["abilities"]
    for i in range(0, len(abilities)):
        poke.p_abilities += abilities[i]["ability"]["name"].capitalize()

        if i != len(abilities) - 1:
            poke.p_abilities += "\n"

    # get info
    all_info = species_data["flavor_text_entries"]
    poke.p_info = "*NULL*"
    for i in all_info:
        if i["language"]["name"] == "en":
            poke.p_info = i["flavor_text"]
            break

    # get image_link
    poke.image_link = general_data["sprites"]["front_default"]

    # get stats
    stats = general_data["stats"]
    for i in range(0, len(stats)):
        stat_name = stats[i]["stat"]["name"]
        stat_value = stats[i]["base_stat"]
        poke.p_total_stats += stat_value
        poke.p_stats[stat_name] = stat_value

    # get evolution chain
    evolution_chain = []
    chain_data = evolution_data["chain"]
    while chain_data != "":
        evolution_chain.append(chain_data["species"]["name"])
        try:
            chain_data = chain_data["evolves_to"][0]
        except:
            break
    for i in range(0, len(evolution_chain)):
        poke.p_evolution_chain += evolution_chain[i].capitalize()

        if i > len(evolution_chain) - 2:
            break
        else:
            poke.p_evolution_chain += "\n"

    # get rarity
    try:
        rarity = aerialace_cache_manager.cached_rarity_data[poke.p_name.lower()]
        if rarity == "mythical" or rarity == "legendary" or rarity == "ultra beast":
            poke.p_rarity = rarity.capitalize()
        else:
            poke.p_rarity = None
    except:
        poke.p_rarity = None

    return poke

# for getting a random pokemon
async def get_random_poke():

    rand_pokemon_id = random.randint(1, 898)

    poke = await get_poke_by_id(rand_pokemon_id)

    return poke

# for wrapping text
def wrap_text(width, text):
    wrapped_text = ""
    wrapper = TextWrapper(width)
    text_lines = wrapper.wrap(text)
    for line in text_lines:
        wrapped_text += "{line}\n".format(line=line)

    return wrapped_text

async def get_roll(username, upper_limit):
    try:
        if upper_limit == "":
            max_roll = 100
        elif int(upper_limit) < 0:
            raise ValueError()
        else:
            max_roll = int(upper_limit)
    except:
        return "Enter a valid upper index! Like this : ```-aa roll 100```"

    roll_value = random.randint(0, max_roll)

    return "> **{name}** rolled and got {roll} :game_die:".format(name=username, roll=roll_value)

# get parameter from the message
async def get_parameter(msg, removable_command) -> str:
    param = msg
    for cmd in removable_command:
        param = param.replace(cmd, "").strip()

    return param

# returns the winner and loser
async def get_winner_looser(msg):
    param = await get_parameter(msg, ["log_battle", "lb"])
    players = param.split()
    winner, loser = players
    winner, loser = await get_id_from_ping(winner), await get_id_from_ping(loser)

    return [winner, loser]

# returns user id from ping
async def get_id_from_ping(ping):

    user_id = ""
    for i in ping:
        if i.isnumeric():
            user_id = user_id + i

    return user_id

# get random pokemon embed
async def get_random_pokemon_embed(poke_data, server_id, user_id):

    embd = discord.Embed(color=global_vars.NORMAL_COLOR)
    embd.title = "**{0} : {1}**".format(poke_data.p_id, poke_data.p_name)

    description = wrap_text(40, poke_data.p_info)
    embd.description = description
    embd.set_image(url=poke_data.image_link)

    return embd

# get Dex entry embed
async def get_dex_entry_embed(poke_data):
    max_character_width = 40

    if poke_data is None:
        return get_info_embd("Gib pokemon name as a parameter when :/", "> Provide a pokemon name like ```-aa dex aron```", color=global_vars.ERROR_COLOR)

    embd = discord.Embed(color=global_vars.NORMAL_COLOR)
    embd.title = "**{0} : {1}**".format(poke_data.p_id, poke_data.p_name)

    description = wrap_text(max_character_width, poke_data.p_info)
    description += "\n"

    embd.add_field(
        name="Height",
        value="{h} m".format(h=poke_data.p_height),
        inline=True
    )
    embd.add_field(
        name="Weight",
        value="{w} kg".format(w=poke_data.p_weight),
        inline=True
    )
    embd.add_field(
        name="Region",
        value="{r}".format(r=poke_data.p_region),
        inline=True
    )
    embd.add_field(
        name="Type(s)",
        value="{t}".format(t=poke_data.p_types),
        inline=True
    )
    embd.add_field(
        name="Ability(s)",
        value="{a}".format(a=poke_data.p_abilities),
        inline=True
    )
    embd.add_field(
        name="Evolution",
        value="{evolution_chain}".format(evolution_chain=poke_data.p_evolution_chain),
        inline=True
    )

    stats_string = "```"
    stats_string += "HP  : {hp}".format(hp=poke_data.p_stats["hp"]).ljust(11, " ") + "| " + "Sp.Atk : {spatk}".format(spatk=poke_data.p_stats["special-attack"]).ljust(13, " ")
    stats_string += "\n"
    stats_string += "Atk : {atk}".format(atk=poke_data.p_stats["attack"]).ljust(11, " ") + "| " + "Sp.Def : {spdef}".format(spdef=poke_data.p_stats["special-defense"]).ljust(13, " ")
    stats_string += "\n"
    stats_string += "Def : {df}".format(df=poke_data.p_stats["defense"]).ljust(11, " ") + "| " + "Speed  : {spd}".format(spd=poke_data.p_stats["speed"]).ljust(13, " ")
    stats_string += "```"

    embd.add_field(name="Stats (Total : {total_stats})".format(total_stats=poke_data.p_total_stats), value=stats_string, inline=False)

    embd.description = description
    embd.set_image(url=poke_data.image_link)

    if poke_data.p_rarity is not None:
        embd.set_footer(text=f"Rarity : {poke_data.p_rarity}")

    return embd

# get invite embed
async def get_invite_embed(embd, color):
    invite_link = global_vars.INVITE_LINK
    thumbnail_link = global_vars.AVATAR_LINK

    embd.title = "Invite Aerial Ace to your server"
    embd.description = ("[Click the link and select the server to add to.]({link})".format(link=invite_link))
    embd.set_thumbnail(url=thumbnail_link)
    embd.color = color

    return embd

# get battle acceptance
async def get_battle_acceptance(client, message, winner, loser):

    check_id = ""

    if str(message.author.id) == winner:
        check_id = loser
    elif str(message.author.id) == loser:
        check_id = winner
    else:
        await message.channel.send("> Who are you to do this. Let the players log their battles.")
        return "notapplicable"

    # send battle log request
    log_msg = await message.channel.send("Logging <@{winner}>'s win over <@{loser}>. Click the checkmark to accept."
                                         .format(winner=winner, loser=loser))

    accept_emoji = "☑️"

    await log_msg.add_reaction(accept_emoji)

    def check(_reaction, _user):
        return str(_user.id) == check_id and str(_reaction.emoji) == accept_emoji

    try:
        await client.wait_for("reaction_add", timeout=10.0, check=check)
    except:
        return "notaccepted"
    else:
        return "accepted"

# returns a info embed
async def get_info_embd(title, error, color, footer=None):
    embd = discord.Embed()

    embd.colour = color
    embd.title = title
    embd.description = error

    if footer is not None:
        embd.set_footer(text=footer)

    return embd

# check if any message is a rare catch message
async def determine_rare_catch(msg):

    """
    1. Determine if catch message, else return None
    2. Determine shiny catch or normal catch.
    3. Shiny Catch : 
        remove all the unnecessary text
        get the catch data
        return the catch data
    4. Normal Catch : 
        Remove the shit
        Get required data from the remaining message
        return the data
    """

    message = msg.replace("!", "").replace(".", "").replace("♂️", "").replace("♀️", "")     # remove the shit
    message_words = message.split()  

    is_shiny = True
    catch_info = {}

    catch_keywords = ["Congratulations", "You", "caught", "a", "level"]
    shiny_keywords = ["These", "colors", "seem", "unusual"]


    # determines whether this message is a catch message by checking the presence of the all catch keywords
    for catch_keyword in catch_keywords:
        if catch_keyword not in message_words:
            return None # Not a catch message

    
    # determine shiny catch by checking the presence of all the shiny keywords
    for shiny_keyword in shiny_keywords:
        if shiny_keyword not in message_words:
            is_shiny = False

    extra_text = ["Shiny streak reset.", "Added to Pokédex. You received 35 Pokécoins!", "These colors seem unusual... ✨", ".", "!", "(", ")"]

    info_text = msg
    for extra in extra_text:
        info_text = info_text.replace(extra, "")

    info_words = info_text.split()

    catch_info["user"] = info_words[1] 
    catch_info["level"] = info_words[6]
    catch_info["pokemon"] = ""
    catch_info["type"] = ""

    if info_words[-1].isnumeric():
        info_words.remove(info_words[-1])

    pokemon_name_words = info_words[7:]

    if is_shiny:
        catch_info["type"] = "shiny"
        catch_info["pokemon"] = ""
        for i in pokemon_name_words:
            catch_info["pokemon"] = catch_info["pokemon"] + f"{i.capitalize()} "
        catch_info["pokemon"] = catch_info["pokemon"].strip()
        return catch_info
    else:
        catch_info["pokemon"] = ""
        for i in pokemon_name_words:
            catch_info["pokemon"] += i.strip().capitalize() + " "
            try:
                if aerialace_cache_manager.cached_rarity_data[i.lower()] in ["legendary", "mythical", "ultra beast"]:
                    catch_info["type"] = "rare"
                    catch_info["pokemon"] = catch_info["pokemon"].strip()
                    break
            except:
                continue

    if catch_info["type"] == "":
        return None

    return catch_info

async def get_rare_catch_embd(_message, _ping, _pokemon, _level, _type):

    # TODO : Add some kind of rare and shiny sighting counter

    embd = discord.Embed(colour=global_vars.RARE_CATCH_COLOR)

    if _type == "rare":
        embd.title = ":star2: Rare Catch Detected :star2:"
        embd.description = f"{_ping} caught a level {_level} `{_pokemon}`\n"
        embd.set_image(url=global_vars.JIRACHI_WOW)
    elif _type == "shiny":
        embd.title = ":star2: Shiny Catch Detected :star2:"
        embd.description = f"{_ping} caught a level {_level} **SHINY** `{_pokemon}`\n"
        embd.set_image(url=global_vars.PIKA_SHOCK)

    embd.description += f"Congratulations :tada: :tada:\n"

    try:
        await _message.pin()
        embd.description += "This catch was pinned to this channel"
    except:
        embd.description += "Unable to pin this catch :/"

    _date = datetime.date.today().strftime("%d %b %y")
    _time_object = datetime.datetime.now(datetime.timezone.utc)
    _time = _time_object.strftime("%I:%M %p UTC")

    embd.set_footer(text=f"{_date} at {_time}")

    return embd

async def get_bot_info_embd():
    embd = discord.Embed(colour=global_vars.NORMAL_COLOR)
    embd.title = "ABOUT - Aerial Ace"
    embd.description = "Aerial Ace = Poketwo helper bot + pokedex"
    embd.add_field(
        name="Support Server",
        value=f"[Link to the support server]({global_vars.SUPPORT_SERVER_LINK})",
        inline=False
    )
    embd.add_field(
        name="Get Started",
        value="Ping the bot or type `-aa help`",
        inline=False
    )
    embd.add_field(
        name="Source Code",
        value="Complete Source Cod, of Aerial Ace is public.\nThis means anyone can host their own version of the bot.\nHowever check the license before proceeding with running your own version of the bot\n[Link to the github repository](https://github.com/Devanshu19/)",
        inline=False
    )

    embd.set_thumbnail(url=global_vars.AVATAR_LINK)

    return embd

# for waiting
async def waiter(_time: float):
    await asyncio.sleep(_time)
    print("Times up")