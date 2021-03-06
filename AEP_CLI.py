import platform
import subprocess
import json
import os
from prompt_toolkit.history import FileHistory

from aep_sdk import API

import click
import click_repl

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
    if not ctx.invoke(login, config="config.json"):
        print("No config created, Upload aborted")
        return False
    if len(filename) < 1:
        print("There must be at least one file to upload. Upload aborted")
        return
    if datasetid is None:
        print("There must be a datasetID in order to upload. Upload aborted")
        return
    api = API('config.json')
    try:
        api.upload(filename, datasetid)
    except FileNotFoundError:
        print("One of the files does not seem to be a valid file path, please check your file paths")


@cli.command(help="Optionally receives a filepath and attempts to login using the JSON information stored in "
                  "the file. If no filepath is given, user will be prompted to create one. Choosing to do so "
                  "will open a new JSON in the current working directory with the proper formatting.")
@click.option('--config', nargs=1)
def login(config):
    if config is None:
        createConfig(None)
    else:
        try:
            with open(config, "r") as f:
                print(f.readlines())
                return True
        except FileNotFoundError:
            created = createConfig(config)
            if created:
                print("Attempt login operation")
                return True
            else:
                print("A valid configuration file must be present "
                      "in order to perform Adobe Experience Platform API calls.")
                return False
            # pass


@cli.command(help="Checks the status of a batch with the given ID (Requires Login).")
@click.argument('batchid', nargs=1)
def check_batch(batchid):
    if batchid == "":
        print("There must be a batch ID to check")
        return
    api = API('config.json')
    api.report(batchid)
    print(batchid)

@cli.command(help="Checks if a given dataset ID is valid to the account (Requires Login).")
@click.argument('datasetid', nargs=1)
def validate(datasetid):
    if datasetid == "":
        print("There must be a dataset ID to check")
        return
    api = API('config.json')
    if api.validate(datasetid):
        print("This dataset ID is valid")
        return
    else:
        print("This is not a valid dataset ID")
        return


@cli.command(help="Gets the list of dataset IDs associated with your AEP account, limited to the number given"
                  " and filtered according to the optional string given")
@click.argument('limit', nargs=1)
@click.option('-s', '--search', 'string')
def getdatasetids(limit, string):
    print(limit)
    api = API('config.json')
    print(api.dataId(limit))
    if string is not None:
        print(string)

def createConfig(str):
    if str is None:
        msg = "Since you have not provided a config file path, would you like to create one now" \
              " in your current working directory?"
    else:
        msg = str + " does not seem to be a valid file path.\n Would you like to create a" \
               " new config file in the working directory now?"
    if click.confirm(msg, default=False):
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
        return True
    else:
        return False

if __name__ == "__main__":
    cli(obj={})
