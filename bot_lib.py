from twitchio.ext import commands
import twitchio.errors as ioerr
import json
import asyncio
import time


def generate_default_conf():
    confg = {
        "token" : "",
        "channels" : [""],
        "authorized" : [""],
        "admin" : [""],
        "slot" : [""],
        "gol_count" : [],
        }
    with open("confg.json", 'w') as f:
        json.dump(confg, f)

    print('json config file created. Please enter values on config.json file before use')
    input()
    exit()


def log_action(logs):
    logs = (f'{time.localtime().tm_hour}:{time.localtime().tm_min} [{time.localtime().tm_mday}/{time.localtime().tm_mon}]\t'\
           f'{logs}')
    
    print(logs)
    with open('logs.txt', 'a') as f:
        f.write(f'{logs}\n')
    return 0


def switch(command_status, command_name, ctx: commands.Context):
    if command_status[0] == True:
        command_status[0] = False
        log_action(f'{command_name} command turned off by {ctx.author.name}')
    elif command_status[0] == False:
        command_status[0] = True
        log_action(f'{command_name} command turned on by {ctx.author.name}')


def all_on(all_commands, ctx: commands.Context):
    for i in all_commands:
        all_commands[i][0] = True
            
    log_action(f'All commands turned on by {ctx.author.name}')
    return 0


def all_off(all_commands, ctx: commands.Context):
    for i in all_commands:
        all_commands[i][0] = False

    log_action(f'All commands turned off by {ctx.author.name}')
    return 0


async def cooldown(command_on_cooldown):
    command_on_cooldown[0] = True
    await asyncio.sleep(command_on_cooldown[1])
    command_on_cooldown[0] = False


def json_file_save(file_name, dic):
    with open(file_name, 'w') as f:
        json.dump(dic, f)


async def wait_for_response(self, ctx: commands.Context, user_to_wait):
    while True:
        message = await self.wait_for('message')
        try:
            author = message[0].author.name
            if author == user_to_wait:
                response = message[0].content.lower().split(' ')
                break
        except AttributeError:
            pass
        except TimeoutError:
            return None
    return response


async def ban_user(self, ctx: commands.Context, bot, token: str, channel: str, user: str, duration: int, reason: str, command: str):
    try:
        users = await bot.fetch_users(names=[channel, user])
        await users[0].timeout_user(token=token, moderator_id=self.user_id, user_id=users[1].id, duration=duration, reason=reason)
        log_action(f'User banned ({command}): {user} <{channel}> <{duration}>')
    except ioerr.HTTPException:
        try:
            users = await bot.fetch_users(names=[channel, user])
            await users[0].timeout_user(token=token, moderator_id=self.user_id, user_id=users[1].id, duration=duration, reason=reason)
            log_action(f'User banned ({command}): {user} <{channel}> <{duration}>')
        except ioerr.HTTPException as error:
            log_action(f'User not banned due to an error ({command}): {user} <{channel}> <{duration} \n {error}')