import platform
import subprocess
import json
import os

import click


@click.group()
def main():
    """
    CLI tool for uploading data to Adobe Experience Platform
    """
    pass


@main.command()
@click.argument('filename', nargs=-1)
@click.argument('datasetid', nargs=1)
@click.option('--config', 'config')
def upload(filename, datasetid, config):
    login(config)
    print(datasetid)
    for str in filename:
        try:
            with open(str) as f:
                print(f.readlines())
        except FileNotFoundError:
            print(str, " does not seem to be a valid file path, please check your file paths")
        print(str)


#@main.command()
#@click.option('--config', nargs=1)
def login(config):
    if config is None:
        createConfig(None)
    else:
        try:
            with open(config, "r") as f:
                print(f.readlines())
        except FileNotFoundError:
            created = createConfig(config)
            if created:
                print("Attempt login operation")
            else:
                print("A valid configuration file must be present in order to perform Adobe Experience Platform API calls")
                return
            pass


@main.command()
@click.argument('batchid', nargs=1)
def check_batch(batchid):
    print(batchid)


@main.command()
@click.argument('limit', nargs=1)
@click.option('-s', '--search', 'string')
def getdatasetids(limit, string):
    print(limit)
    if string is not None:
        print(string)


def createConfig(str):
    if str is None:
        msg = "Since you have not provided a config file path, would you like to create one now" \
              " in your current working directory?"
    else:
        msg = str + " does not seem to be a valid file path, would you like to create a " \
               "new config file in the working directory now?"
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
            subprocess.call(['xdg-open', 'config.json'])
        return True
    else:
        return False

if __name__ == "__main__":
    main()
