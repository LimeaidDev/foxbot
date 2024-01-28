import json
import random
import traceback
import time
import values
import discord
from discord.ext import commands
from discord import app_commands
import datetime
import openai
import urllib
import pickle as pkl
import os
import psycopg2

# openai bullshit
GPT_API_KEY = open("secrets/GPT_API_KEY", "r").read()
openai.api_key = GPT_API_KEY
global chat_log
chat_log = []



# i dont know how to variable
global presys_message

global settingslist

# main loop
def run():
    tools = [
        {
            "type": "function",
            "function": {
                "name": "imagine_in_conv",
                "description": "makes images when users ask for one or want to add on too a current one using DALLE. Images are made with the provided prompt through DALLE and sent in chat. For example someone can ask for 'an image of a fox' and then later ask 'give him a scarf' which you then adjust the prompt accordingly. Be sure to distinguish wether the user is contiuing the conversation or asking for modifications so that you dont make an image a user doesnt want",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "prompt": {
                            "type": "string",
                            "description": "a description of an image the user wants",
                        },
                        "response": {
                            "type": "string",
                            "description": "What you would say after making the image"
                        }
                    },
                    "required": ["prompt", "response"],
                },
            }
        }
    ]
    # refreshes settings while bot is running so users can change settings in real time
    def settingsrefresh():
        global temp
        global model
        global prefix
        global adminprefix
        global admins
        temp = int(open("data/settingsdata/temp").read())
        model = str(open("data/settingsdata/model").read())
        prefix = str(open("data/settingsdata/prefix").read())
        adminprefix = "pa!"
        admins = [
            1020563958781984788
        ]
    # Updates and preps the system prompt with new info so the bot is aware of its suroundings
    def systemrefresh(ServerName, ServerOwner, ChannelName, ChannelTopic, username, userid):
        global chat_log
        global presys_message
        # Outdated data saving from a darker time
        # systemfile = str(open("data/settingsdata/system").read())
        # if os.path.isfile(f"data/systems/{userid}"):
            # userprompt = str(open(f"data/systems/{userid}").read())
        # else:
            # userprompt = str(open(f"data/systems/polly.txt").read())
        conn = psycopg2.connect(host="kashin.db.elephantsql.com", dbname="hustfxta", user="hustfxta",
                                password="lRntwmDTkAUNU-CsYTqKgFYsujLv_2X-", port=5432)
        cur = conn.cursor()

        cur.execute("""SELECT * FROM system_prompts WHERE serverid = %s; """, [str(userid)])

        promptfetch = cur.fetchone()

        if promptfetch is None:
            userprompt = ""
        else:
            userprompt = promptfetch[1]
        cur.close()
        presys_message = rf"""{userprompt}


    Consider the following in your responses:
    - Be conversational
    - Write spoilers using spoiler tags.
    - You can mention people by adding a @ before their name.
    - Format text using markdown.

    Information about your environment:
     - The server you are in is called: {ServerName}
     - The server is owned by: {ServerOwner}
     - The channel you are in is called: #{ChannelName}
     - The channel topic provided is: {ChannelTopic}
     - and the user that messaged you is {username} but call them by the name given in there messages

    You can use this information about the chat participants in the conversation in your replies. Use this information to answer questions, or add flavor to your responses.
    You are not a personal assistant and cannot complete tasks for people
    DO NOT include your own username or timestamps in your resposes. They are there to provide context to the conversation.
    Make sure to greet users diffrently depening on how long they have been away
    The usernames provided are Display names so dont use @ symbolises"""  # For
        sys_message = {"role": "system", "content": presys_message}
        chat_log.insert(0, sys_message)
        print(chat_log)
    # outdated from when you could dm the bot, might remove
    def systemrefreshdm(Username, userid):
        systemfile = str(open("data/settingsdata/system").read())
        if os.path.isfile(f"data/systems/{userid}"):
            userprompt = str(open(f"data/systems/{userid}").read())
        else:
            userprompt = ""
        presys_message = rf"""{str(open(f"data/systems/{systemfile}").read())}

    The Following is how the user wants you to behave. If there is no text then the user has not set up a custom prompt.

    {userprompt}

    Past this point is not set by the user

    Consider the following in your responses:
    - Be conversational
    - Write spoilers using spoiler tags.
    - You can mention people by adding a @ before their name.
    - Format text using markdown.

    Information about your environment:
     - Your in {Username}'s DM

    Heres a list of the commands users can use from you:
     - {prefix}vari
     - {prefix}complete
     - {prefix}vitals
     - {prefix}help
     - {prefix}imagine
     - {prefix}voice
    You can use this information about the chat participants in the conversation in your replies. Use this information to answer questions, or add flavor to your responses.
    You are not a personal assistant and cannot complete tasks for people
    Remember to keep your messages appropriate and respectful. Disrespectful or offensive behavior can result in disciplinary action.
    And finally, don't forget to have fun! Discord is a great place to meet new people, make new friends, and enjoy some quality conversation.
    DO NOT include your own username or timestamps in your resposes. They are there to provide context to the conversation.
    Make sure to greet users diffrently depening on how long they have been away
    The usernames provided are Display names so dont use @ symbolises"""  # For main channels
        sys_message = {"role": "system", "content": presys_message}
        chat_log.insert(0, sys_message)


    bot = commands.Bot(command_prefix="f!", intents=discord.Intents.all())
    @bot.event
    # What happens when the bot starts
    async def on_ready():
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"{len(bot.guilds)} Servers"))
        print("foxbot is up!")
        # syncing commands
        try:
            synced = await bot.tree.sync()
            print(f"Synced {len(synced)}")
        except Exception as e:
            print(e)
        print('Servers connected to:')
        for guild in bot.guilds:
            print(guild.name)
            print(f"ID: {guild.id}")

    @bot.tree.command(name="changelog", description="Shows changes in diffrent versions")
    @app_commands.choices(version=[
        discord.app_commands.Choice(name='Prerelese 1', value=1), discord.app_commands.Choice(name='Prerelese 2', value=2)])
    async def changelog(interaction: discord.Interaction, version: discord.app_commands.Choice[int]):
        if version.value == 1:
            embed = discord.Embed(title="Foxbot Prerelese 1",
                                  description="""**Begining of version tracking**\n
                                  **New Updates**
                                  * Added /changelog
                                   * Shows changes for each version\n
                                  **Fixes**
                                  * System prompts are now store on a server keeping settings the same even when code is updated""")
            await interaction.response.send_message(
                embed=embed, ephemeral=True)
        if version.value == 2:
            embed = discord.Embed(title="Foxbot Prerelese 2",
                                  description="""
                                  **New Updates**
                                  * Set max chatbot response tokens to 25""")
            await interaction.response.send_message(
                embed=embed, ephemeral=True)


    # How popular is foxbot
    @bot.tree.command(name="servers", description="Shows number of servers")
    async def servers(interaction: discord.Interaction):
        await interaction.response.send_message(f"I'm in **{len(bot.guilds)}** servers", ephemeral=False)

    # Test if the bot is alive
    @bot.tree.command(name="hello", description="Say hello to your furry friend")
    async def hello(interaction: discord.Interaction):
        await interaction.response.send_message("hey there", ephemeral=True)

    # i guess you could use foxbot to timeout a user but litrealy any other bot can do that
    @bot.tree.command(name='timeout', description="Timeout a user for a specific amount of time")
    async def timeout(interaction: discord.Interaction, member: discord.Member, days: int = 0, hours: int = 0, minutes: int = 0, seconds: int = 30):
        try:
            # Check if the user invoking the command has the 'Moderate Members' permission
            if not interaction.user.guild_permissions.moderate_members:
                raise discord.ext.commands.MissingPermissions(['moderate_members'])

            # Your existing code for the command logic goes here
            await member.timeout(datetime.timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds), reason=f"Requested by {interaction.user.global_name}")
            await interaction.response.send_message(f"✅ I've timed out {member.mention} for {days} days, {hours} hours, {minutes} minutes, and {seconds} seconds.",
                                                    ephemeral=True)

        except discord.errors.Forbidden:
            await interaction.response.send_message(f"⛔ I can't timeout this user due to insufficient permissions.",
                                                    ephemeral=True)
        except discord.ext.commands.MissingPermissions as e:
            await interaction.response.send_message(
                f"⛔ You are missing the required permissions to use this command", ephemeral=True)
        except:
            await interaction.followup.send(content=f"An error occurred ```{traceback.format_exc()}```")
    # pulls a random image from a website
    @bot.tree.command(name='randomimage', description="Pulls a random image from the web")
    async def randomimage(interaction: discord.Interaction, width: int = 1920, height: int = 1080):
        urllib.request.urlretrieve(f"https://random.imagecdn.app/{width}/{height}", "random.png")
        await interaction.response.send_message(file=discord.File("random.png"), ephemeral=False)
    # have an algorithm spit out fresh plagiarism
    @bot.tree.command(name='imagine', description="Uses machine learning models to generate images")
    @app_commands.describe(model="Choose a image generation model")
    @app_commands.choices(model=[
        discord.app_commands.Choice(name='dall-e-3', value=1),
        discord.app_commands.Choice(name='dall-e-2', value=2),
    ])
    async def imagine(interaction: discord.Interaction, prompt: str, model: discord.app_commands.Choice[int]):
        await interaction.response.defer()
        try:
            response = await openai.Image.acreate(
                model=model.name,
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                n=1,
            )
            # Remove loading message
            urllib.request.urlretrieve(response["data"][0]["url"], f'{interaction.user.id}1.png')
            try:
                await interaction.followup.send(content=f"""# {prompt}""", files=[discord.File(f'{interaction.user.id}1.png')])
            except:
                await interaction.channel.send(content=f"""*Original message was deleted*\n# {prompt}""", files=[discord.File(f'{interaction.user.id}1.png')])
            os.remove(f'{interaction.user.id}1.png')
        except openai.error.InvalidRequestError:
            await interaction.followup.send(content=f"""This prompt was rejected.""")

    @bot.tree.command(name="vari", description="Make variations of an image")
    async def hello(interaction: discord.Interaction, image: discord.Attachment):
        try:
            await interaction.response.defer()
            print(image)
            await image.save(f'{interaction.user.id}variin.png')
            response = await openai.Image.acreate_variation(
                image=open(f'{interaction.user.id}variin.png', "rb"),
                n=4,
                size="256x256",
            )

            urllib.request.urlretrieve(response["data"][0]["url"], f'{interaction.user.id}vari1.png')
            urllib.request.urlretrieve(response["data"][1]["url"], f'{interaction.user.id}vari2.png')
            urllib.request.urlretrieve(response["data"][2]["url"], f'{interaction.user.id}vari3.png')
            urllib.request.urlretrieve(response["data"][3]["url"], f'{interaction.user.id}vari4.png')
            try:
                await interaction.followup.send(files=[discord.File(f'{interaction.user.id}variin.png'), discord.File(f'{interaction.user.id}vari1.png'), discord.File(f'{interaction.user.id}vari2.png'), discord.File(f'{interaction.user.id}vari3.png'), discord.File(f'{interaction.user.id}vari4.png')])
            except:
                await interaction.channel.send("*Original message was deleted*" ,files=[discord.File(f'{interaction.user.id}variin.png'), discord.File(f'{interaction.user.id}vari1.png'), discord.File(f'{interaction.user.id}vari2.png'), discord.File(f'{interaction.user.id}vari3.png'), discord.File(f'{interaction.user.id}vari4.png')])

            os.remove(f'{interaction.user.id}vari1.png')
            os.remove(f'{interaction.user.id}vari2.png')
            os.remove(f'{interaction.user.id}vari3.png')
            os.remove(f'{interaction.user.id}vari4.png')
        except:
            try:
                await interaction.followup.send(content=f"Sorry, that was on us 😅. Use /feedback if this keeps happening")
                recenterror = traceback.format_exc()
            except:
                await interaction.channel.send(f"*Original message was deleted*\nAn error occurred ```{traceback.format_exc()}```")
    @bot.tree.command(name="mock", description="Make it seem like another user said something")
    async def mock(interaction: discord.Interaction, user:discord.Member, text:str):
        await interaction.response.send_message("This feature is tempraraly disabled", ephemeral=False)
        
        # webhooks = await interaction.channel.webhooks()
        # webhook = discord.utils.get(webhooks, name=f"foxbot")
        # if webhook is None:
        #    webhook = await interaction.channel.create_webhook(name=f"foxbot")
        # await interaction.response.send_message("Mock message sent", ephemeral=True)
        # await webhook.send(text, username=user.display_name, avatar_url='{}'.format(user.avatar))

    @bot.tree.command(name="anon", description="Anonymously send a message")
    async def anon(interaction: discord.Interaction, text: str):
        await interaction.response.send_message("This feature is tempraraly disabled", ephemeral=False)
        # webhooks = await interaction.channel.webhooks()
        # webhook = discord.utils.get(webhooks, name=f"foxbot")
        # if webhook is None:
        #    webhook = await interaction.channel.create_webhook(name=f"foxbot")
        # await interaction.response.send_message("Anonymous message sent", ephemeral=True)
        # await webhook.send(text, username="Anonymous", avatar_url="https://sandstormit.com/wp-content/uploads/2021/06/incognito-2231825_960_720-1.png")

    @bot.tree.command(name='rps', description="Play Rock Paper Scissors with a CPU")
    @app_commands.describe(choice="Choose Rock, Paper, Or Scissors")
    @app_commands.choices(choice=[
        discord.app_commands.Choice(name='Rock', value=1),
        discord.app_commands.Choice(name='Paper', value=2),
        discord.app_commands.Choice(name='Scissors', value=3)])
    async def imagine(interaction: discord.Interaction, choice: discord.app_commands.Choice[int]):
        cpu = random.choice(['Rock', 'Paper', 'Scissors'])
        def is_win(player, opponent):
            if (player == 'Rock' and opponent == 'Scissors') or (player == 'Scissors' and opponent == "Paper") or (
                    player == 'Paper' and opponent == 'Rock'):
                return True


        if choice.name == cpu:
            await interaction.response.send_message(f'# Its a tie!\n**{interaction.user.display_name}**\n{choice.name}\n\n**CPU**\n{cpu}')
            return


        if is_win(choice.name, cpu):
            await interaction.response.send_message(f'# {interaction.user.display_name} Wins!\n**{interaction.user.display_name}**\n{choice.name}\n\n**CPU**\n{cpu}')
            chat_log.append({"role": "user",
                             "content": f"System: {interaction.user.display_name} played rock paper scissors with you and won"})

        if not is_win(choice.name, cpu):
            await interaction.response.send_message(f'# CPU Wins!\n**{interaction.user.display_name}**\n{choice.name}\n\n**CPU**\n{cpu}')
            chat_log.append({"role": "user",
                             "content": f"(System: {interaction.user.display_name} played rock paper scissors with you and lost"})

    @bot.tree.command(name='chatbotsystem', description="Chnage the system prompt of the chatbot")
    async def chatsys(interaction: discord.Interaction):
        conn = psycopg2.connect(host="kashin.db.elephantsql.com", dbname="hustfxta", user="hustfxta",
                                password="lRntwmDTkAUNU-CsYTqKgFYsujLv_2X-", port=5432)
        cur = conn.cursor()

        cur.execute("""SELECT * FROM system_prompts WHERE serverid = %s; """, [str(interaction.guild.id)])

        promptfetch = cur.fetchone()
        print(promptfetch)
        if promptfetch is None:
            default = ""
        else:
            default = promptfetch[1]
        cur.close()
        #if os.path.isfile(f"data/systems/{interaction.guild.id}"):
            #default = str(open(f"data/systems/{interaction.guild.id}").read())
        #else:
            #default = ""
        class SystemModal(discord.ui.Modal, title="Chatbot System Prompt"):
            message = discord.ui.TextInput(
                style=discord.TextStyle.long,
                label="Prompt",
                max_length=300,
                required=False,
                default=default,
                placeholder="Input a prompt"
            )

            async def on_submit(self, interaction: discord.Interaction):
                if interaction.user.guild_permissions.moderate_members:
                    conn = psycopg2.connect(host="kashin.db.elephantsql.com", dbname="hustfxta", user="hustfxta",
                                            password="lRntwmDTkAUNU-CsYTqKgFYsujLv_2X-", port=5432)
                    cur = conn.cursor()
                    print(interaction.guild.id)
                    print(self.message.value)
                    print(cur.mogrify("""INSERT INTO system_prompts (serverid, prompt) VALUES (%s, %s); """,
                                      (str(interaction.guild.id), self.message.value)))

                    cur.execute("""DELETE FROM system_prompts WHERE serverid = %s; """, [str(interaction.guild.id)])
                    cur.execute("""INSERT INTO system_prompts (serverid, prompt) VALUES (%s, %s); """, (str(interaction.guild.id), self.message.value))
                    conn.commit()
                    cur.close()

                    #if len(self.message.value) > 0:
                       #file = open(f"data/systems/{interaction.guild.id}", "w+")
                        #file.write(self.message.value)
                    await interaction.response.send_message(
                        f"Prompt Updated",
                        ephemeral=True, delete_after=3)
                    #else:
                        #if os.path.isfile(f"data/systems/{interaction.guild.id}"):
                            #os.remove(f"data/systems/{interaction.guild.id}")
                        #await interaction.response.send_message(
                            #f"Prompt Updated",
                            #ephemeral=True, delete_after=3)

        if interaction.user.guild_permissions.moderate_members:
            system_modal = SystemModal()
            system_modal.user = interaction.user
            await interaction.response.send_modal(system_modal)
        else:
            await interaction.response.send_message(
                f"You can't modify this servers chatbot",
                ephemeral=True, delete_after=3)

    @bot.tree.command(name='chatlogreset', description="Reset the chatlog in the current channel")
    async def clreset(interaction: discord.Interaction):
        deletebutton = discord.ui.Button(label="Delete chatlog", style=discord.ButtonStyle.danger)
        cancelbutton = discord.ui.Button(label="Nevermind", style=discord.ButtonStyle.secondary)

        async def delete_button_callback(interaction):
            if os.path.isfile(f"data/chatlogdata/{interaction.channel.id}"):
                os.remove(f"data/chatlogdata/{interaction.channel.id}")
                await interaction.response.edit_message(content="Chatlog deleted", view=None, delete_after=3)
            else:
                await interaction.response.edit_message(content="There was no chatlog to delete", view=None, delete_after=3)

        async def cancel_button_callback(interaction):
            await interaction.response.edit_message(content="Nothing was changed", view=None, delete_after=3)


        deletebutton.callback = delete_button_callback
        cancelbutton.callback = cancel_button_callback

        view = discord.ui.View()
        view.add_item(deletebutton)
        view.add_item(cancelbutton)

        if interaction.user.guild_permissions.moderate_members:
            await interaction.response.send_message(f"Are you sure you want to delete the chatlog for this channel? All conversations will be deleted\n\nCanceling <t:{int(time.time()) + 15}:R>", view=view, delete_after=15, ephemeral=True)
        else:
            await interaction.response.send_message("You can't modify this servers chatbot", delete_after=3, ephemeral=True)





    class FeedbackModal(discord.ui.Modal, title="Send us your feedback"):
        fb_title = discord.ui.TextInput(
            style=discord.TextStyle.short,
            label="What are you having issue with?",
            required=True,
        )
        message = discord.ui.TextInput(
            style=discord.TextStyle.long,
            label="Can you describe the issue further?",
            max_length=500,
            required=True,
        )
        contact = discord.ui.select(
            placeholder="Please select Yes or No",
            options=[
                discord.SelectOption(
                    label="Yes"
                ),
                discord.SelectOption(
                    label="No"
                )
            ]
        )

        async def on_submit(self, interaction: discord.Interaction):
            channel = interaction.guild.get_channel(1178673345663881276)

            embed = discord.Embed(title="New Feedback", description=f"**{self.fb_title.value}**\n\n{self.message.value}\n\n")

            embed.set_author(name=f'@{interaction.user}')

            await interaction.response.send_message(f"Thank you, {interaction.user.display_name}. We will try to look into this", ephemeral=True)
            await interaction.guild.get_channel(1178673345663881276).send(embed=embed)




    @bot.tree.command(name="feedback", description="Got a problem? Submit feedback so we can fix it.")
    async def feedback(interaction: discord.Interaction):
        feedback_modal = FeedbackModal()
        feedback_modal.user = interaction.user
        await interaction.response.send_modal(feedback_modal)



    async def on_error(self, interaction: discord.Interaction, error):
        print()


    @bot.event
    async def on_message(message):
        if not message.author.bot:
            if bot.user in message.mentions or message.content.lower() == "hey poly" or str(
                    message.channel.type) == "private" and not message.author.bot:
                async with message.channel.typing():
                    try:
                        with open("data/chatlogdata/" + str(message.channel.id), "rb") as f:
                            chat_log = pkl.load(f)
                    except:
                        chat_log = []
                    loop = True
                    while loop:
                        if len(chat_log) >= 20:
                            del chat_log[0]
                        if len(chat_log) <= 20:
                            loop = False
                    global user_message

                    try:
                        settingsrefresh()
                        systemrefresh(message.guild.name, message.guild.owner.display_name, message.channel.name,
                                      message.channel.topic, message.author.name, message.guild.id)
                    except AttributeError:
                        systemrefreshdm(message.author.display_name, message.author.id)

                    user_message = message.author.display_name + ': ' + message.content.replace(
                        "<@1061881210818801674> ", "")

                    current_date_time = datetime.datetime.now()
                    formatted_date_time = current_date_time.strftime("%Y-%m-%d %H:%M:%S")

                    chat_log.append({"role": "user", "content": f"({formatted_date_time}) {user_message}"})
                    os.system("cls")
                    chat_log_readable = '\n'.join(str(item) for item in chat_log)
                    chat_log_readable = chat_log_readable.encode('utf-8', 'replace')
                    os.system("cls")
                    systemrefresh(message.guild.name, message.guild.owner.display_name, message.channel.name,
                                  message.channel.topic, message.author.name, message.guild.id)
                    with open("data/chatlogdata/" + str(message.channel.id), "wb+") as f:
                        pkl.dump(chat_log, f)
                    sys_message = {"role": "system", "content": presys_message}
                    chat_log.insert(0, sys_message)
                    response = await openai.ChatCompletion.acreate(
                        model=model,
                        messages=chat_log,
                        temperature=temp,
                        tools=tools,
                        max_tokens=25
                    )

                    del chat_log[0]
                    try:
                        if response['choices'][0]['message']['tool_calls'][0]['type'] == "function":
                            try:
                                waittext = await message.channel.send("*making image...*", reference=message)
                            except:
                                waittext = await message.channel.send("*making image...*")
                            arguments = json.loads(response['choices'][0]['message']['tool_calls'][0]['function']['arguments'])
                            prompt = arguments['prompt']
                            imageresponse = arguments['response']
                            print(arguments)
                            with open("data/chatlogdata/" + str(message.channel.id), "rb") as f:
                                chat_log = pkl.load(f)

                            chat_log.append({"role": "user",
                                             "content": f"({formatted_date_time}) System: {message.author.display_name} talked to foxbot to generat a image of {prompt}"})
                            chat_log.append({"role": "user",
                                             "content": f"{imageresponse}"})
                            try:
                                response = await openai.Image.acreate(
                                    model="dall-e-3",
                                    prompt=prompt,
                                    size="1792x1024",
                                    quality="standard",
                                    n=1,
                                )
                                # Remove loading message
                                urllib.request.urlretrieve(response["data"][0]["url"], f'{message.author.id}1conv.png')
                                await waittext.delete()
                                try:
                                    await message.channel.send(content=f"""{imageresponse}""", files=[discord.File(f'{message.author.id}1conv.png')], reference=message)
                                except:
                                    await message.channel.send(content=f"""{imageresponse}""",
                                                               files=[discord.File(f'{message.author.id}1conv.png')])

                            except openai.error.InvalidRequestError:
                                await message.channel.send(content=f"""This prompt was rejected.""")
                    except:
                        assisstant_response = response['choices'][0]['message']['content']

                        try:
                            try:
                                await message.channel.send(assisstant_response.strip("\n").strip(), reference=message)
                            except:
                                await message.channel.send(assisstant_response.strip("\n").strip())
                        except:
                            try:
                                await message.channel.send(f"""Sorry, that was on us 😅. Use /feedback if this keeps happening
                                for the devs:
                                ```{traceback.format_exc()}```""", reference=message)
                                recenterror = traceback.format_exc()
                            except:
                                await message.channel.send(f"*Replying to {message.author.display_name}: {user_message}*\n\nSorry, that was on us 😅. Use /feedback if this keeps happening")
                            print(response['choices'][0]['message']['tool_calls'][0]['function']['arguments'])

                        chat_log.append({"role": "assistant", "content": f"{assisstant_response}"})

                        with open("data/chatlogdata/" + str(message.channel.id), "wb+") as f:
                            pkl.dump(chat_log, f)

                        chat_log_readable = '\n'.join(str(item) for item in chat_log)
                        chat_log_readable = chat_log_readable.encode('utf-8', 'replace')
                        open("data/chatlogdata/" + str(message.channel.id) + "_readable.txt", "wb+").write(
                            chat_log_readable)
                        os.system("cls")

    bot.run(values.DIS_TKN)

if __name__ == "__main__":
    run()
