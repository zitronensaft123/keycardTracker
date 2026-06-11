from rich.console import Console
from rich.columns import Columns
from rich.panel import Panel

console = Console()


def main():
    stats = [
        Panel("", title="", style="bold green"),
    ]

    console.print(Columns(stats))
main()

#ef printStatScreen():

