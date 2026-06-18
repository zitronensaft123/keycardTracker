from datetime import datetime

from rich import box
from rich.prompt import Prompt
from rich.align import Align
from rich.console import Console, Group
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax
from rich.table import Table
from rich.live import Live
import click
import art
import time

import db

db.initDB()
db.updatePrices()

promptItems = [
    "Physical Bitcoin",
    "Roler Submariner gold wrist watch"
]

aliases = {
    "Physical Bitcoin" : "BTC",
    "Roler Submariner gold wrist watch" : "Roler"
}

console = Console()

def createProgressBar(current, goal):
    progress = Progress(
        TextColumn(formatNumber(db.getNetWorth())),
        BarColumn(bar_width=70, complete_style="green", finished_style="bold green"),
        TextColumn(formatNumber(500000000))
    )

    taskID = progress.add_task("tracking", total=goal)

    progress.update(taskID, completed=current)

    return progress

def formatNumber(number):
    return f"{number:,}".replace(",", ".")

#create new Panel
def createPanel(ratio):
    panel = Table.grid(expand=True)

    if ratio == 1:
        panel.add_column(ratio=1)
        panel.add_column(ratio=2)
    else:
        panel.add_column(ratio=2)
        panel.add_column(ratio=1)

    return panel

def printDashboard():

    stats = db.getStats()

    itemRows = []

    for fullName, quantity in stats["itemsFound"].items():
        displayName = aliases.get(fullName, fullName)

        itemRows.append(f"* {displayName:<10} x{quantity}")

    itemPanelContent = "\n".join(itemRows)

    # the header ascii art 
    topPanel = Panel.fit(art.text2art("KEYCARD TRACKER", font="sky free"), title="BETA ", subtitle="=")

    midPanel = createPanel(1)

    midPanel.add_row(
        Panel(itemPanelContent + "\n", title="Items"),
        Panel(
            f"{'Money Earned:':<15} {formatNumber(stats['moneyEarned'])} ₽\n"
            f"{'Money Spent:':<15} {formatNumber(stats['moneySpent'])} ₽\n"
            f"{'Profit:':<15} {formatNumber(stats['revenue'])} ₽", 
            title="Statistics"
    ))

    bottomPanel = Panel(createProgressBar(db.getNetWorth(), 500000000), title="Goal")

    contents = Group(
        topPanel,
        midPanel,
        bottomPanel
    )

    layout = Align.left(contents)

    console.clear()
    console.print(layout)

def printPrompt():

    selection = Prompt.ask("Select option: (h to list avaiable commands)", choices=["r", "u", "h", "s", "e"], default="r")
    console.print()

    foundItems = {}

    if selection == "r":
        length = Prompt.ask("How long was ur raid? (write as min:sec)")
        console.print()

        cost = Prompt.ask("What did the Blackcard approximately cost? (Full Price)", default=formatNumber(4500000))
        console.print()


        for item in promptItems:
            foundItems[item] = printItemPrompt(item)

    elif selection == "u":
        money = Prompt.ask("How much RUB do u currently possess?")
        db.addNetWorthEntry(money)
        return
    
    elif selection == "h":
        console.print(" r: Add new Raid entry \n u: Update current Net Worth \n s: Settings \n e: Exit \n")
        print("Press any key to continue")
        click.getchar()
        return
    elif selection == "s":
        settingSelection = Prompt.ask("c: Change goal", choices=["c"])
        if settingSelection == "c":
            newGoal = Prompt.ask("What do u want to change the goal to?")
        print("\n Done")
        return
    else:
        console.print("bye")
        exit()

    # !TODO: make a function that adds keycars to the found items
    card = Prompt.ask("Found any Keycard? (UNFINISHED, wont do anything)", choices=["None","Black", "Blue", "Green", "Violet", "Red"], default="None")
    console.print()

    console.print("----------- added (⊃‿⊂) -----------")
    time.sleep(1)
    console.clear()
    db.addNewRaid(length, foundItems, cost)

def printItemPrompt(itemname):
    quantity = Prompt.ask("How many " + itemname + " did u find?", default="0")
    console.print()
    return quantity

def main():
    console.clear()
    while(True):
        printDashboard()
        printPrompt()
        db.conn.commit
main()