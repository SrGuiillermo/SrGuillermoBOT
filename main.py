import bot_lib as lib
from twitchio.ext import commands
import twitchio.errors as ioerr
import json


try:
    with open('confg.json', 'r') as f:
        confg = json.load(f)
except FileNotFoundError:
    lib.generate_default_conf()


commands_status = {
    'console_msg_status' : [False],
    'namess_com_status' : [True],
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

    #Show twitch chat messages on console
    async def event_message(self, message):
        split_msg = message.content.lower().split(' ')

        if message.echo:
            return
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
                try:
                    timeout_duration = split_msg[2]
                    if int(timeout_duration) >= 300:
                        timeout_duration = 300
                    try:
                        channel = split_msg[3]
                    except IndexError:
                        channel = ctx.channel.name
                except ValueError:
                    timeout_duration = 300
                    channel = split_msg[2]
                except IndexError:
                    timeout_duration = 300
                    channel = ctx.channel.name

            try:
                users = await bot.fetch_users(names=[channel, target])
                await users[0].timeout_user(token=confg['token'], moderator_id=self.user_id, user_id=users[1].id, duration=int(timeout_duration), reason='')
                lib.log_action(f'Namess command used by {ctx.author.name} : {target} timeout {timeout_duration}s <{channel}>')
            except ioerr.HTTPException:
                lib.log_action(f'Namess command used by {ctx.author.name} : target ({target}) was a moderator or a broadcaster or was already banned <{channel}>')
                return 1

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
                    lib.log_action(f'Nunban command used by {ctx.author.name} : target ({target}) was not banned <{channel}>')


if __name__ == "__main__":
    bot = Bot()
    bot.run()