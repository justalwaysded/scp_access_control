import os

def clear_screen():
    # screen clear for windows ('cls') and linux/macOS ('clear')
    os.system('cls' if os.name == 'nt' else 'clear')

def pause():
    input("\nPress RETURN to continue...")