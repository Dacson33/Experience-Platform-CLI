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
    # Set the name for the default configuration file to seek in the working directory
    ctx.obj["defaultConfig"] = 'config.json'
    if ctx.invoked_subcommand is None:
        ctx.invoke(repl)
    elif ctx.invoked_subcommand == "login":
       pass
    else:
        ctx.obj["API"] = aep_sdk.API(ctx.obj["defaultConfig"])


def repl():
    prompt_kwargs = { 'history': FileHistory(os.path.expanduser('~/.repl_history'))}
    click_repl.repl(click.get_current_context(), prompt_kwargs)


@cli.command(help="Exit the REPL")
def quit():
    click_repl.exit()


@cli.command(help="Exit the REPL")
def exit():
    click_repl.exit()


@cli.command(help="Receives a filename or list of filenames and dataset ID and attempts to upload the file/files "
                  "to the given dataset ID in the Adobe Experience Platform. Will attempt login before upload.")
@click.argument('filename', nargs=-1)
@click.argument('datasetid', nargs=1)
@click.pass_context
def upload(ctx, filename, datasetid):
    """
    Receives a filename or list of filenames and a dataset ID to upload them to.
    Will attempt login and creation of config.json if needed.
    :param ctx: Context object associated with the click CLI, will contain the API object
    :param filename:
    :param datasetid:
    """
    if len(filename) < 1:
        print("There must be at least one file to upload. Upload aborted")
        return False
    APIReady = checkForAPI(ctx, "Upload")
    if not APIReady:
        return False
    if datasetid is None:
        print("There must be a datasetID in order to upload. Upload aborted")
        return False
    if not "API" in ctx.obj:
        print("An error occured when creating the API handler object, "
              "please check your config file. Upload aborted")
        return False
    api = ctx.obj["API"]
    for str in filename:
        try:
            api.upload(filename, datasetid)
        except FileNotFoundError:
            print(str, " does not seem to be a valid file path, please check your file paths")
            continue
        print(str)


@cli.command(help="Optionally receives a filepath and attempts to login using the JSON information stored in "
                  "the file. If no filepath is given, user will be prompted to create one. Choosing to do so "
                  "will open a new JSON in the current working directory with the proper formatting.")
@click.option('--config', nargs=1)
@click.pass_context
def login(ctx, config):
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
    If no file is provided or the file path is invalid, user will be given the option to create
    a config file in the working directory via a template that will automatically open.
    :param ctx: Context object associated with the click CLI, will contain the API object
    :param config: Optionally passed in from the command line as a file path to the config file
    :return Returns false if login failed
    """
    # If the api object already exists they have logged in, so we will prompt them in case it was accidental
    if "API" in ctx.obj:
        if click.confirm("You are already logged in, would you like to login again? "):
            pass
        else:
            return False
    if config is None:
        config = ctx.obj["defaultConfig"]
    try:
        api = aep_sdk.API(config)
        api.access()
        ctx.obj["API"] = api
    except FileNotFoundError:
        created = createConfig(ctx, config)
        if not created:
            return False
        else:
            try:
                api = aep_sdk.API(ctx.obj["defaultConfig"])
                api.access()
                ctx.obj["API"] = api
            except Exception as e:
                print("The following error occured when creating the API object: ")
                print(e)
                print("Usually this is caused by an error in the config file")
                return False
        # pass
    except Exception as e:
        print("The following error occured when creating the API object: ")
        print(e)
        print("Usually this is caused by an error in the config file")
        return False
    return True


@cli.command(help="Checks the status of a batch with the given ID (Requires Login).")
@click.argument('batchid', nargs=1)
@click.pass_context
def check_batch(ctx, batchid):
    """
    Checks the current status of the batch with the given id.
    Will attempt login and creation of a config file if needed
    :param ctx: Context object associated with the click CLI, will contain the API object
    :param batchid: ID of the batch to be queried (required)
    :return: None
    """
    APIReady = checkForAPI(ctx, "Check Batch")
    if not APIReady:
        return False
    if batchid == "":
        print("There must be a batch ID to check")
        return False
    api = ctx.obj["API"]
    api.report(batchid)


@cli.command(help="Gets the list of dataset IDs associated with your AEP account, limited to the number given"
                  " and filtered according to the optional string given")
@click.argument('limit', nargs=1)
@click.option('-s', '--search', 'string')
@click.pass_context
def getdatasetids(ctx, limit, search):
    """
    Retrieve a list of datasetIDs associated with this user (limited to the limit number)
    Search them and find any that match the search term (if one is provided), else print them
    :param ctx: Context object associated with the click CLI, will contain the API object
    :param limit: How many datasetIDs to retrieve (required)
    :param search: Term to use when searching the names and datasetIDs received (optional)
    :return: None
    """
    APIReady = checkForAPI(ctx, "Get DatasetIDs")
    if not APIReady:
        return False
    api = ctx.obj["API"]
    print(api.dataId(limit))
    if search is not None:
        print(search)


@cli.command(help="Checks if a given dataset ID is valid to the account (Requires Login).")
@click.argument('datasetid', nargs=1)
@click.pass_context
def validate(ctx, datasetid):
    """
    Checks if the given datasetID is valid
    :param ctx: Context object associated with the click CLI, will contain the API object
    :param datasetid: DatasetID to be checked for validity
    :return: Whether the datasetID is valid or not
    """
    APIReady = checkForAPI(ctx, "Validate")
    if not APIReady:
        return False
    if datasetid == "":
        print("There must be a dataset ID to check")
        return
    api = ctx.obj["API"]
    if api.validate(datasetid):
        print("This dataset ID is valid")
        return
    else:
        print("This is not a valid dataset ID")
        return


def checkForAPI(ctx, msg, filename="config.json"):
    """
    Check for a valid API object and attempt instantiation if none exists.
    :param ctx: Context object associated with the click CLI, will contain the API object
    :param msg: The type of call being made when checkForAPI is called. Will be used in the error message
    :param filename: File path of the configuration file. To attempt API creation from if no API exists
    :return: Boolean of whether a valid API object has already been instantiated
    """
    if not "API" in ctx.obj:
        if not ctx.invoke(login, config=filename):
            print(msg + " aborted")
            return False
        else:
            return True

def createConfig(ctx, configFile):
    """
    creates a new config file in the working directory if the user wants to, else returns to the CLI
    :param ctx: Context object associated with the click CLI, will contain the API object
    :param configFile: file path to the config file, may be None depending on where it is called from
    :return: Boolean of whether the user created a new config file or not
    """
    msg = "After searching for " + configFile + " it does appear to exist.\n\n" \
          "Would you like to create a new config.json file in your working directory now?"
    if click.confirm(msg, default=False):
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
            subprocess.call(['open', ctx.obj["defaultConfig"]])
        elif platform.system() == 'Windows':
            os.startfile(ctx.obj["defaultConfig"])
        else:
            subprocess.call('xdg-open', ctx.obj["defaultConfig"])
        input("Press Enter when you are done editing your config file")
        return True
    else:
        print("A valid configuration file must be present "
              "in order to perform Adobe Experience Platform API calls.")
        return False

if __name__ == "__main__":
    cli(obj={})
