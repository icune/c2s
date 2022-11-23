"""Just prints nice results for data analysis."""
from typing import List

import click

from gmatch.analytics.load_data import load_data
from termcolor import colored

from gmatch.gmatch.items import GoogleItem

data: List[GoogleItem] = None


@click.group()
def cli():
    pass

@cli.command()
def list():
    print("\n".join([d.company.name for d in data]))

@cli.command()
@click.argument("company", required=True)
def search(company: str):
    matched = [c for c in data if company.lower() in c.company.name.lower()]
    if len(matched) > 2:
        raise Exception(
            "There are more than one matches for your input:\n\n%s" % "\n".join([m.company.name for m in matched])
        )
    mc = matched[0]
    print(colored(mc.company.name + ' :: ' + mc.company.address, "red"))
    print()
    for sl in mc.search_list:
        print(colored(sl.title, "green"))
        print(colored(sl.href, "blue"))
        print(sl.short_description)
        print()



if __name__ == "__main__":
    data = load_data()
    try:
        cli()
    except Exception as e:
        print(colored("ERROR\n", "red"))
        print(e)
