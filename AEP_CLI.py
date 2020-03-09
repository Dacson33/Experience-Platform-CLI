import click

@click.group()
def main():
    """
    CLI tool for uploading data to Adobe Experience Platform
    """
    pass

@main.command()
#@click.argument('upload')
@click.argument('filename', nargs=-1)
@click.argument('datasetid', nargs=1)
def upload(filename, datasetid):
    print(datasetid)
    for str in filename:
        print(str)

@main.command()
@click.argument('config', nargs=1)
def login(config):
    print(config)

if __name__ == "__main__":
    main()