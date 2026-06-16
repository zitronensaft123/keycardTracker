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
import art
import time

import db

db.initDB()
db.updatePrices()

promptItems = [
    "Physical Bitcoin",
    "Roler Submariner gold wrist watch"
]

console = Console()

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

    # the header ascii art 
    topPanel = Panel.fit(art.text2art("KEYCARD TRACKER", font="sky free"), title="v1.0", subtitle="=")

    midPanel = createPanel(1)

    midPanel.add_row(
        Panel(str(stats["itemsFound"]), title="Items"),
        Panel("Money Earned: " + f"{stats['moneyEarned']:,}".replace(",", "."), title="Statistics")
    )

    bottomPanel = createPanel(2)

    bottomPanel.add_row(
        Panel("", title="API"),
        Panel("", title="Goal")
    )

    contents = Group(
        topPanel,
        midPanel,
        bottomPanel
    )

    layout = Align.left(contents)

    console.clear()
    console.print(layout)

def printPrompt():

    selection = Prompt.ask("Enter new Raid?", choices=["Y", "n"], default="Y")
    console.print()

    foundItems = {}

    if selection == "Y":
        length = Prompt.ask("How long was ur raid? (write as min:sec)")
        console.print()

        cost = Prompt.ask("What did the Blackcard approximately cost? (Full Price)", default="4500000")
        console.print()


        for item in promptItems:
            foundItems[item] = printItemPrompt(item)

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