import platform
import subprocess
import json
import os
from prompt_toolkit.history import FileHistory

import click
import click_repl

import aep_sdk


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """
    CLI Utility for uploading data to the Adobe Experience Platform
    """
    if ctx.invoked_subcommand is None:
        ctx.invoke(repl)


def repl():
    prompt_kwargs = { 'history': FileHistory(os.path.expanduser('~/.repl_history'))}
    click_repl.repl(click.get_current_context(), prompt_kwargs)


@cli.command(help="Exit the REPL")
def quit():
    click_repl.exit()


@cli.command(help="Exit the REPL")
def exit():
    click_repl.exit()


"""
Receives a filename or list of filenames and a dataset ID to upload them to. 
Will attempt login and creation of config.json if needed. 
"""
@cli.command(help="Receives a filename or list of filenames and dataset ID and attempts to upload the file/files "
                  "to the given dataset ID in the Adobe Experience Platform. Will attempt login before upload.")
@click.argument('filename', nargs=-1)
@click.argument('datasetid', nargs=1)
@click.pass_context
def upload(ctx, filename, datasetid):
    if not "API" in ctx.obj:
        if not ctx.invoke(login, config="config.json"):
            print("No config created, Upload aborted")
            return False
        else:
            pass
    if len(filename) < 1:
        print("There must be at least one file to upload. Upload aborted")
        return
    if datasetid is None:
        print("There must be a datasetID in order to upload. Upload aborted")
        return
    for str in filename:
        try:
            with open(str) as f:
                print(f.readlines())
        except FileNotFoundError:
            print(str, " does not seem to be a valid file path, please check your file paths")
            continue
        print(str)

"""
Receives a file path for a configuration file of the form
{
    "api_key": "",
    "client_secret": "",
    "ims_org": "",
    "jwt_token": "",
    "sub": "",
    "secret": ""
}
If no file is provided or the filepath is invalid, user will be given the option to create
a config file in the working directory via a template that will automatically open.
"""
@cli.command(help="Optionally receives a filepath and attempts to login using the JSON information stored in "
                  "the file. If no filepath is given, user will be prompted to create one. Choosing to do so "
                  "will open a new JSON in the current working directory with the proper formatting.")
@click.option('--config', nargs=1)
@click.pass_context
def login(ctx, config):
    if config is None:
        created = createConfig(ctx, None)
        return handleConfigCreated(ctx, created)
    else:
        try:
            with open(config, "r") as f:
                print(f.readlines())
                return True
        except FileNotFoundError:
            created = createConfig(ctx, config)
            return handleConfigCreated(ctx, created)
            # pass

def handleConfigCreated(ctx, created):
    if created:
        print("Attempt login operation")
        ctx.obj["access_token"] = "token made"
        return True
    else:
        print("A valid configuration file must be present "
              "in order to perform Adobe Experience Platform API calls.")
        return False

@cli.command(help="Checks the status of a batch with the given ID (Requires Login).")
@click.argument('batchid', nargs=1)
@click.pass_context
def check_batch(ctx, batchid):
    if batchid == "":
        print("There must be a batch ID to check")
        return
    print(batchid)


@cli.command(help="Gets the list of dataset IDs associated with your AEP account, limited to the number given"
                  " and filtered according to the optional string given")
@click.argument('limit', nargs=1)
@click.option('-s', '--search', 'string')
@click.pass_context
def getdatasetids(ctx, limit, string):
    print(limit)
    if string is not None:
        print(string)

def createConfig(ctx, str):
    if str is None:
        msg = "Since you have not provided a config file path, would you like to create one now" \
              " in your current working directory?"
    else:
        msg = "After searching your working directory for " + str + "it does appear you have a config file.\n " \
              "Would you like to create a new config file in the now?"
    if click.confirm(msg, default=False):
        complete = None
        print("Opening new json file with formatted template")
        data = {}
        data["api_key"] = ""
        data["client_secret"] = ""
        data["ims_org"] = ""
        data["jwt_token"] = ""
        data["sub"] = ""
        data["secret"] = ""
        with open("config.json", 'w') as outfile:
            json.dump(data, outfile, indent=4)
        if platform.system() == 'Darwin':
            subprocess.call(['open', 'config.json'])
        elif platform.system() == 'Windows':
            os.startfile('config.json')
        else:
            subprocess.call('xdg-open', 'config.json')
        while(complete == None):
            complete = click.prompt("Press any key when config file is completed", type=any)
        return True
    else:
        return False

if __name__ == "__main__":
    cli(obj={})
