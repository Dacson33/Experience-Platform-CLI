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
def upload(filename, datasetid):
    print(datasetid)
    for str in filename:
        print(str)


@main.command()
@click.argument('config', nargs=1)
def login(config):
    print(config)


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


if __name__ == "__main__":
    main()
