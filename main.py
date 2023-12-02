import bot_lib as lib
from twitchio.ext import commands
import twitchio.errors as ioerr
import json
import random


try:
    with open('confg.json', 'r') as f:
        confg = json.load(f)
except FileNotFoundError:
    lib.generate_default_conf()


commands_status = {
    'console_msg_status' : [False],
    'namess_com_status' : [True],
    'gol_com_status' : [True],
    'slot_com_status' : [True],
}

commands_cooldowns = {
    "gol_on_cooldown" : [False],
    "slot_on_cooldown" : [False],
}

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(
            token = confg['token'],
            prefix = '$',
            initial_channels = confg['channels']
            )

    #Loggin
    async def event_ready(self):
        print(f'Logged in as {self.nick}')
        return await super().event_ready()

    async def event_message(self, message):
        split_msg = message.content.lower().split(' ')

        if message.echo:
            return
        #Print message on console if active
        if commands_status['console_msg_status'][0] == True:
            print(f'<{message.channel.name}> {message.author.name} : {message.content}')
        await self.handle_commands(message)


    #Switches
    #Current status of commands
    @commands.command()
    async def status(self, ctx: commands.Context):
            if ctx.author.name in confg['admin']:
                print()
                print(f'Console: {commands_status["console_msg_status"][0]} [$swconsole]')
                print(f'Namess command: {commands_status["namess_com_status"][0]} [$swnamess]')
                print(f'Gol command: {commands_status["gol_com_status"][0]} [$swgol]')
                print(f'Slot command: {commands_status["slot_com_status"][0]} [$swslot]')
                print()

    #Console
    @commands.command()
    async def swconsole(self, ctx: commands.Context):
        if ctx.author.name in confg['admin']:
            lib.switch(commands_status['console_msg_status'], 'Console logs', ctx)

    #Namess
    @commands.command()
    async def swnamess(self, ctx: commands.Context):
        if ctx.author.name in confg['admin']:
            lib.switch(commands_status['namess_com_status'], 'Namess', ctx)
    
    #Slot
    @commands.command()
    async def swslot(self, ctx: commands.Context):
        if ctx.author.name in confg['admin']:
            lib.switch(commands_status['slot_com_status'], 'Slot', ctx)

    #Gol
    @commands.command()
    async def swgol(self, ctx: commands.Context):
        if ctx.author.name in confg['admin']:
            lib.switch(commands_status['gol_com_status'], 'Gol', ctx)

    #All Off
    @commands.command()
    async def alloff(self, ctx: commands.Context):
        if ctx.author.name in confg['admin']:
            lib.all_off(commands_status, ctx)

    #All On
    @commands.command()
    async def allon(self, ctx: commands.Context):
        if ctx.author.name in confg['admin']:
            lib.all_on(commands_status, ctx)


    #Commands
    #Namess command: timeout user
    @commands.command()
    async def namess(self, ctx: commands.Context):
        if commands_status['namess_com_status'][0] == True:
            if ctx.message.author.name in confg['authorized']:
                split_msg = ctx.message.content.split(' ')
                target = split_msg[1]
                try:  #$namess {user} {duration} {channel} form
                    timeout_duration = split_msg[2]
                    if int(timeout_duration) >= 300:
                        timeout_duration = 300
                    try: 
                        channel = split_msg[3]
                    except IndexError: #$namess {user} {duration} form
                        channel = ctx.channel.name
                except ValueError: #$namess {user} {channel} form
                    timeout_duration = 300
                    channel = split_msg[2]
                except IndexError: #$namess {user} form
                    timeout_duration = 300
                    channel = ctx.channel.name

            try: 
                #Fetch channel and user to timeout
                users = await bot.fetch_users(names=[channel, target]) 
                #Timeout and log the action
                await users[0].timeout_user(token=confg['token'], moderator_id=self.user_id, user_id=users[1].id, duration=int(timeout_duration), reason='')
                lib.log_action(f'Namess command used by {ctx.author.name} : {target} timeout {timeout_duration}s <{channel}>')
            except ioerr.HTTPException:
                lib.log_action(f'Namess command used by {ctx.author.name} : target ({target}) was a moderator or a broadcaster or was already banned <{channel}>')

    #Nunban command: unban user
    @commands.command()
    async def nunban(self, ctx: commands.Context):
        if commands_status['namess_com_status'][0] == True:
            if ctx.message.author.name in confg['authorized']:
                split_msg = ctx.message.content.split(' ')
                target = split_msg[1]
                try:
                    channel = split_msg[2]
                except IndexError:
                    channel = ctx.author.name
                
                try:
                    users = await bot.fetch_users(names=[channel, target])
                    await users[0].unban_user(token=confg['token'], moderator_id=self.user_id, user_id=users[1].id)
                    lib.log_action(f'Nunban command used by {ctx.author.name} : target ({target}) <{channel}>')
                except ioerr.HTTPException:
                    lib.log_action(f'Nunban command used by {ctx.author.name} : target ({target}) was not unbanned <{channel}>')

    #Gol
    @commands.command()
    async def gol(self, ctx: commands.Context):
        if commands_status["gol_com_status"][-1] == True:
            if commands_cooldowns["gol_on_cooldown"][-1] == False:
                confg["gol_count"] += 1
                lib.json_file_save(file_name="confg.json", dic=confg)
                await ctx.send("GOLAZOOO DE ELMILLOR!! Ya van {} Elm: 🙁 Maradona: 💀".format(confg["gol_count"]))
                await lib.cooldown(commands_cooldowns["gol_on_cooldown"], 3)

    #Slot
    @commands.command()
    async def slot(self, ctx: commands.Context):
        if commands_status['slot_com_status'][-1] == True:
            if commands_cooldowns['slot_on_cooldown'][-1] == False:
                #Get win/lose 25% chance of win
                slot_chance = random.randint(1, 4)
                if slot_chance == 2: #if win
                    slot_win = random.randint(0, len(confg["slot"]) - 1)
                    await ctx.send('{} ㅤ👉 ㅤ[ {} | {} | {} ]ㅤ WIN Pog Esperando un usuario peepoEvil'
                                   .format(ctx.author.name, confg["slot"][slot_win], confg["slot"][slot_win], confg["slot"][slot_win]))
                    
                    timeout_user = await lib.wait_for_response(self, ctx)

                    try:
                        users = await bot.fetch_users(names=[ctx.channel.name, timeout_user[0]])
                        await users[0].timeout_user(token=confg['token'], moderator_id=self.user_id, user_id=users[1].id, duration=300, reason='')
                        lib.log_action(f'Slot command used by {ctx.author.name} (win) : target ({ctx.author.name}) <{ctx.channel.name}>')
                    except ioerr.HTTPException:            
                        lib.log_action(f'Slot command used by {ctx.author.name} (win) : target ({ctx.author.name}) was not banned <{ctx.channel.name}>')
                else: #if lose
                    slot_random = random.sample(confg["slot"], 3)
                    await ctx.send('{} ㅤ👉 ㅤ[ {} | {} | {} ]ㅤ LOSE -1m PepeGiggle'
                                   .format(ctx.author.name, slot_random[0], slot_random[1], slot_random[2]))
                    
                    try:
                        users = await bot.fetch_users(names=[ctx.channel.name, ctx.author.name])
                        await users[0].timeout_user(token=confg['token'], moderator_id=self.user_id, user_id=users[1].id, duration=60, reason='')
                        lib.log_action(f'Slot command used by {ctx.author.name} (lose) <{ctx.channel.name}>')
                    except ioerr.HTTPException:
                        lib.log_action(f'Slot command used by {ctx.author.name} (lose) : target was not banned <{ctx.channel.name}>')

                await lib.cooldown(commands_cooldowns["slot_on_cooldown"], 15) 


if __name__ == "__main__":
    bot = Bot()
    bot.run()