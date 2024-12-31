from colorama import Fore, Style, init

# Initialize colorama
init()

class TerminalColors:
    WARNING = Fore.YELLOW
    ENDC = Style.RESET_ALL
    INFO = Fore.CYAN
    PENALTY = Fore.MAGENTA

def print_colored(text, color:TerminalColors):
    print(f"{color}{text}{TerminalColors.ENDC}")

