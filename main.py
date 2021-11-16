import discord
import os
import aerialace

client = discord.Client()
guild = None

@client.event
async def on_ready():
	print("Logged in as {0.user}".format(client))

@client.event
async def on_message(message):

	#initialization
	global guild
	if guild == None : 
		guild = message.guild

	if(message.author == client.user):
		return

	msg = message.content.lower()
	member = message.author
	user_id = int(message.author.id)
	nickname = member.display_name

	#say hello
	if msg.startswith("-aa hello") or msg.startswith("-aa alola") or msg.startswith("-aa hola") or msg.startswith("-aa henlu") or msg.startswith("-aa hi"):
		await message.channel.send("> Alola **{name}**".format(name = nickname))
		return

	#rolling
	if msg.startswith("-aa roll"):
		max_roll = 100

		try:
			max_roll_str = aerialace.get_parameter(msg, "-aa roll")
			
			if max_roll_str == "":
				max_roll = 100
			else:
				max_roll = int(max_roll_str)
		except:
			await message.channel.send("Enter a valid upper index! Like this : ```-aa roll 100```")
			return

		roll = aerialace.roll(max_roll)

		await message.channel.send("> **{name}** rolled and got {roll} :game_die:".format(name = nickname, roll = roll))
		return 

	#Random Pokemon
	if(msg.startswith("-aa rp")) or msg.startswith("-aa rand_poke"):
		
		try:
			rand_poke = aerialace.get_random_poke()
		except Exception as excp:
			await message.channel.send("> Some error occured while fetching random pokemon, the details have been send to the appropriate peeps")
			print("--Error while fetching random pokemon : {e}".format(e = excp))
			return

		reply = aerialace.get_random_pokemon_embed(discord.Embed(), rand_poke, discord.Color.blue())

		await message.channel.send(embed = reply)
		return

	#search for pokemon using index
	if(msg.startswith("-aa dex")):

		param = aerialace.get_parameter(msg, "-aa dex")
		pokeData = None

		try:
			pokeData = aerialace.get_poke_by_id(param)
		except Exception as excp:
			await message.channel.send("> Mhan, that pokemon was not found in the pokedex, if you think this pokemon should be there in the dex, dm DevGa.me#0176")
			print("--Error occured while showing a dex entry : {e}".format(e = excp))
			return

		reply = aerialace.get_dex_entry_embed(discord.Embed(), pokeData, discord.Color.blue())
		
		await message.channel.send(embed = reply)
		return

	#command not found
	if msg.startswith("-aa "):
		await message.channel.send("> -aa what? That command doesn't exist! \n> See all the available commands by using ```-aa help```")
	

token = os.environ['TOKEN']

client.run(token)
