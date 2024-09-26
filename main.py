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
    'duel_com_status' : [True],
}

commands_cooldowns = {
    'gol_on_cooldown' : [False, 3],
    'slot_on_cooldown' : [False, 15],
    'duel_on_cooldown' : [False, 5],
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
                print(f'Duel command: {commands_status["duel_com_status"][0]} [$swduel]')
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

    #Duel
    @commands.command()
    async def swduel(self, ctx: commands.Context):
        if ctx.author.name in confg['admin']:
            lib.switch(commands_status['duel_com_status'], 'Duel', ctx)

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
                target = split_msg[1].strip('@')
                default_timeout = 300
                try:  #$namess {user} {duration} {channel} form
                    timeout_duration = split_msg[2]
                    if int(timeout_duration) >= default_timeout:
                        timeout_duration = default_timeout
                    try: 
                        channel = split_msg[3]
                    except IndexError: #$namess {user} {duration} form
                        channel = ctx.channel.name
                except ValueError: #$namess {user} {channel} form
                    timeout_duration = default_timeout
                    channel = split_msg[2]
                except IndexError: #$namess {user} form
                    timeout_duration = default_timeout
                    channel = ctx.channel.name

                await lib.ban_user(self, ctx, bot, confg['token'], channel, target, timeout_duration, '', 'namess command')


    #Nunban command: unban user
    @commands.command()
    async def nunban(self, ctx: commands.Context):
        if commands_status['namess_com_status'][0] == True:
            if ctx.message.author.name in confg['authorized']:
                split_msg = ctx.message.content.split(' ')
                target = split_msg[1].strip('@')
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
        if commands_status['gol_com_status'][-1] == True:
            if commands_cooldowns['gol_on_cooldown'][0] == False:
                confg['gol_count'] += 1
                lib.json_file_save(file_name='confg.json', dic=confg)
                await ctx.send('GOLAZOOO DE ELMILLOR!! Ya van {} Elm: 🙁 Maradona: 💀'.format(confg['gol_count']))
                await lib.cooldown(commands_cooldowns['gol_on_cooldown'])


    #Slot
    @commands.command()
    async def slot(self, ctx: commands.Context):
        if commands_status['slot_com_status'][-1] == True:
            if commands_cooldowns['slot_on_cooldown'][0] == False:
                lose_timeout = 60
                win_timeout = 300

                #Get win/lose 20% chance of win
                slot_chance = random.randint(0, 4)
                if slot_chance == 2: #if win
                    slot_win = random.randint(0, len(confg['slot'])-1)
                    await ctx.send('{} 👉 [ {} | {} | {} ] WIN Pog Esperando un usuario peepoEvil'
                                   .format(ctx.author.name, confg['slot'][slot_win], confg['slot'][slot_win], confg['slot'][slot_win]))
                    
                    timeout_user = await lib.wait_for_response(self, ctx, ctx.author.name)
                    
                    await lib.ban_user(
                        self, 
                        ctx, 
                        bot, 
                        confg['token'], 
                        ctx.channel.name, 
                        timeout_user[0].strip('@'), 
                        win_timeout, 
                        '', 
                        'slot command win')
                    
                else: #if lose
                    slot_random = random.sample(confg['slot'], 2)
                    slot_random.append(confg['slot'][random.randint(0, len(confg['slot'])-1)])
                    await ctx.send('{} ㅤ👉 [ {} | {} | {} ] LOSE -1m PepeGiggle'
                                   .format(ctx.author.name, slot_random[0], slot_random[1], slot_random[2]))
                    
                    await lib.ban_user(self, ctx, bot, confg['token'], ctx.channel.name, ctx.author.name, lose_timeout, '', 'slot command lose')

                await lib.cooldown(commands_cooldowns['slot_on_cooldown']) 

    
    #Duel
    @commands.command()
    async def duel(self, ctx: commands.Context):
        if commands_status['duel_com_status'][-1] == True:
            if commands_cooldowns['duel_on_cooldown'][0] == False:
                split_msg = ctx.message.content.split(' ')
                user_duel = [ctx.message.author.name, split_msg[1].strip('@')]
                max_timeout = 900

                try:

                    int(split_msg[2])
                    if (await bot.fetch_users(names=[user_duel[1]])) == []: raise ValueError
                    if int(split_msg[2]) > max_timeout: split_msg[2] = max_timeout
                    if int(split_msg[2]) <= 0: split_msg[2] = 1

                    await ctx.send(f'{user_duel[1]}, {user_duel[0]} te desafía por {split_msg[2]} segundos de ban; aceptas? [accept/deny]')
                    
                    while True:
                        message = await self.wait_for('message')
                        try:
                            response = message[0].content.lower().split(' ')
                            if (message[0].author.name == user_duel[1].lower()) and (response[0] == 'accept' or response[0] == 'deny'): break
                            else: pass
                        except AttributeError: pass
                        except TimeoutError: break
                    
                    if response[0] == 'deny': await ctx.send('El duelo fue rechazado')
                    elif response[0] == 'accept':
                        roll = random.randint(0, 100)
                        
                        if roll <= 48:
                            await lib.ban_user(
                            self, ctx, bot, confg['token'], 
                            ctx.channel.name, user_duel[0], 
                            int(split_msg[2]), 
                            '', 
                            'duel command')    
                        elif roll > 48 and roll <= 97:
                            await lib.ban_user(
                            self, ctx, bot, confg['token'], 
                            ctx.channel.name, user_duel[1], 
                            int(split_msg[2]), 
                            '', 
                            'duel command') 
                        elif roll > 97:
                            await lib.ban_user(
                            self, ctx, bot, confg['token'], 
                            ctx.channel.name, user_duel[0], 
                            int(split_msg[2]), 
                            '', 
                            'duel command')

                            await lib.ban_user(
                            self, ctx, bot, confg['token'], 
                            ctx.channel.name, user_duel[1], 
                            int(split_msg[2]), 
                            '', 
                            'duel command')                    
                
                except IndexError:
                    await ctx.send('Estructura del comando: $duel <usuario a desafiar> <segundos>')
                except ValueError:
                    await ctx.send('Introduce el tiempo en segundos')
                except TypeError: pass

            await lib.cooldown(commands_cooldowns['duel_on_cooldown'])

if __name__ == "__main__":
    bot = Bot()
    bot.run()