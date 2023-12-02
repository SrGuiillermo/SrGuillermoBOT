from twitchio.ext import commands
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
        "gol_count" : [""],
        }
    with open("confg.json", "w") as f:
        json.dump(confg, f)

    print("json config file created. Please enter values on config.json file before use")
    input()
    exit()


def log_action(logs):
    logs = (f"{time.localtime().tm_hour}:{time.localtime().tm_min} [{time.localtime().tm_mday}/{time.localtime().tm_mon}]\t"\
           f"{logs}")
    
    print(logs)
    with open("logs.txt", "a") as f:
        f.write(f"{logs}\n")
    return 0


def switch(command_status, command_name, ctx: commands.Context):
    if command_status[0] == True:
        command_status[0] = False
        log_action(f"{command_name} command turned off by {ctx.author.name}")
    elif command_status[0] == False:
        command_status[0] = True
        log_action(f"{command_name} command turned on by {ctx.author.name}")


def all_on(all_commands, ctx: commands.Context):
    for i in all_commands:
        all_commands[i][0] = True
            
    log_action(f"All commands turned on by {ctx.author.name}")
    return 0


def all_off(all_commands, ctx: commands.Context):
    for i in all_commands:
        all_commands[i][0] = False

    log_action(f"All commands turned off by {ctx.author.name}")
    return 0


async def cooldown(command_on_cooldown, cooldown):
    command_on_cooldown[-1] = True
    await asyncio.sleep(cooldown)
    command_on_cooldown[-1] = False


def json_file_save(file_name, dic):
    with open(file_name, "w") as f:
        json.dump(dic, f)


async def wait_for_response(self, ctx: commands.Context):
    original_au = ctx.author.name
    while True:
        message = await self.wait_for("message")
        try:
            author = message[0].author.name
            if author == original_au:
                response = message[0].content.lower().split(" ")
                break
        except AttributeError:
            pass
    return response