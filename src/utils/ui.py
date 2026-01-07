import time
import random
from rich.text import Text
from rich.progress import Progress, ProgressColumn, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.console import Console

console = Console()

class CyberSpinnerColumn(ProgressColumn):
    """15 Custom Cyberpunk Spinner styles"""
    def __init__(self, style_id=None):
        super().__init__()
        self.themes = {
            1: ["(  ● )", "(   ●)", "(  ● )", "( ●   )", "(●    )", "( ●   )"], # Cyber Pulse
            2: ["[ 0101 ]", "[ 1010 ]", "[ 1100 ]", "[ 0011 ]"],             # Binary Breach
            3: ["[>    ]", "[=>   ]", "[==>  ]", "[===> ]", "[====>]"],     # Scanner Beam
            4: ["[*    ]", "[**   ]", "[***  ]", "[**** ]", "[ *** ]"],     # Matrix Flow
            5: ["{ --- }", "{=---=}", "{==--==}", "{=== ===}", "{  --- }"],  # Ghost Grip
            6: [r"| / - \ ", r"/ - \ |", r"- \ | /", r"\ | / -"],               # Satellite Sweep
            7: ["((   ))", "( (  ))", "(  ( ))", "((  ) )", "((   ))"],     # Data Pulse
            8: ["o O o", "O o O", "o O o", "O o O"],                        # Neural Link
            9: ["[#---]", "[##--]", "[###-]", "[####]"],                    # Breach Protocol
            10: ["< . >", "< .. >", "< ... >", "<  .  >"],                  # Phantom Signal
            11: ["░ ▒ ▓ █", "░ ▒ ▓ █", "░ ▒ ▓ █", "░ ▒ ▓ █"],               # Glitch Grid
            12: ["[0x3F]", "[0xA1]", "[0xCC]", "[0xEE]"],                   # Hex Harvest
            13: ["^ v < >", "> ^ v <", "< > ^ v", "v < > ^"],               # Vortex Scan
            14: [r"[ \ ]", r"[ | ]", r"[ / ]", r"[ - ]"],                       # Stealth Radar
            15: ["o-o-o", "-o-o-", "o-o-o", "-o-o-"]                        # Node Connect
        }
        self.style_id = style_id if style_id else random.randint(1, 15)
        self.frames = self.themes.get(self.style_id, self.themes[1])

    def render(self, task=None):
        idx = int(time.time() * 8) % len(self.frames)
        colors = ["green", "cyan", "magenta", "yellow", "bright_blue"]
        color = colors[self.style_id % len(colors)]
        return Text(self.frames[idx], style=f"bold {color}")

def create_cyber_progress(description="[cyan]Processing...[/]", total=None, transient=True):
    """Creates a pre-configured Progress instance with Cyber Spinner"""
    return Progress(
        CyberSpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=40, complete_style="green", finished_style="bold green"),
        TaskProgressColumn() if total else SpinnerColumn(spinner_name="dots", style="bold green"),
        console=console,
        transient=transient
    )
