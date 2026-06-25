# !TODO: fix dashboard panels to be the right size, currently only works if i dont find any other item than BTC, Roler, BlackCard

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

# -----------
versionName = "V1.0 "
# -----------

db.initDB()
db.updatePrices(0)

promptItems = [
    "Physical Bitcoin",
    "Roler Submariner gold wrist watch"
]

aliases = {
    "Physical Bitcoin" : "BTC",
    "Roler Submariner gold wrist watch" : "Roler",
    "TerraGroup Labs keycard (Blue)" : "Keycard (Blue)",
    "TerraGroup Labs keycard (Green)": "Keycard (Green)",
    "TerraGroup Labs keycard (Violet)": "Keycard (Violet)",
    "TerraGroup Labs keycard (Yellow)": "Keycard (Yellow)",
    "TerraGroup Labs keycard (Black)": "Keycard (Black)",
    "TerraGroup Labs keycard (Red)": "Keycard (Red)"
}

console = Console()

def getGoalValue():
    with open("goal.txt") as f:
        return int(f.read())
    
def setGoalValue(goal):
    with open("goal.txt", "w") as f:
        f.write(goal)

def createProgressBar(current, goal):
    progress = Progress(
        TextColumn(formatNumber(db.getNetWorth())),
        BarColumn(bar_width=70, complete_style="green", finished_style="bold green"),
        TextColumn(formatNumber(getGoalValue()))
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
        if fullName == "Physical Bitcoin" or fullName == "Roler Submariner gold wrist watch" or fullName == "TerraGroup Labs keycard (Black)":
            displayName = aliases.get(fullName, fullName)
            itemRows.append(f"* {displayName:<10} x{quantity}")

    itemPanelContent = "\n".join(itemRows)

    # the header ascii art 
    topPanel = Panel.fit(art.text2art("KEYCARD TRACKER", font="sky free"), title=versionName, subtitle="=")

    midPanel = createPanel(1)

    midPanel.add_row(
        Panel(itemPanelContent, title="Items"),
        Panel(
            f"{'Money Earned:':<15} {formatNumber(stats['moneyEarned'])} ₽\n"
            f"{'Money Spent:':<15} {formatNumber(stats['moneySpent'])} ₽\n"
            f"{'Profit:':<15} {formatNumber(stats['revenue'])} ₽", 
            title="Statistics"
    ))

    bottomPanel = Panel(createProgressBar(db.getNetWorth(), getGoalValue()), title="Goal")

    contents = Group(
        topPanel,
        midPanel,
        bottomPanel
    )

    layout = Align.left(contents)

    console.clear()
    console.print(layout)

def printPrompt():

    selection = Prompt.ask("Select option: (h to list avaiable commands)", choices=["r", "u", "h", "d", "e"], default="r")
    console.print()

    foundItems = {}

    if selection == "r":
        length = Prompt.ask("How long was ur raid? (write as min:sec)", default="15:00")
        console.print()

        cost = Prompt.ask("What did the Blackcard approximately cost? (Full Price)", default=formatNumber(4500000))
        console.print()


        for item in promptItems:
            foundItems[item] = printItemPrompt(item)

        card = Prompt.ask("Found any Keycards?", choices=["None","Black", "Blue", "Green", "Violet", "Red", "Yellow"], default="None")
        if card != "None":
            foundItems[db.getKeycardName(card)] = 1
        console.print()

    # update goal
    elif selection == "u":
        money = Prompt.ask("How much RUB do u currently possess?")
        db.addNetWorthEntry(money)
        return
    
    # help menu (print commands)
    elif selection == "h":
        console.print(" r: Add new Raid entry \n u: Update current Net Worth \n d: Dev Options \n e: Exit \n")
        print("Press any key to continue")
        click.getchar()
        return
    
    # some settings currently only changes the goal, maybe gonna add some shit later
    elif selection == "d":
        settingSelection = Prompt.ask(" c: Change goal \n f: Fetch Prices via API, !only use if DB is empty, will bypass 10 min timer! \n b: back \n", choices=["c", "f", "b"])
        if settingSelection == "c":
            newGoal = Prompt.ask("What do u want to change the goal to?")
            setGoalValue(newGoal)
        elif settingSelection == "f":
            print("Fetching...")
            db.updatePrices(1)
        else:
            return
        print("\n Done")
        return
    else:
        console.print("bye")
        exit()

    console.print("----------- added (⊃‿⊂) -----------")
    time.sleep(1)
    console.clear()

    # entry data to database
    db.addNewRaid(length, foundItems, cost)

# prompt how many items that have been found
def printItemPrompt(itemname):
    quantity = Prompt.ask("How many " + itemname + " did u find?", default="0")
    console.print()
    return quantity

def main():
    try:
        console.clear()
        while(True):
            #printDashboard()
            printPrompt()
    except KeyboardInterrupt:
        console.clear()

        console.print("User Interrupt detected, exiting...")

        import sys
        sys.exit(0)
    
#main()