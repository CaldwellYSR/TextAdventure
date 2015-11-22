#!./env/bin/python 

from models import *
from fsm import StateMachine
import sys, os
import textwrap

class controller(object):
    def __init__(self, world=""):
        # Initialize FSM and Player Character
        self.fsm = StateMachine()
        self.t = textwrap.TextWrapper(width=80)
        self.player = Player()
        # Accept world file from command line using -f flag
        if '-f' in sys.argv:
            try:
                f = sys.argv[sys.argv.index('-f') + 1]
            except IndexError:
                print("You didn't include a file")
                sys.exit(0)
            self.world = World(f)
        else:
            self.world = World()
        # Set initial "Zone" to start character in
        self.start_zone = self.world.start()
 
    def _clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print()
        print(self.world.title.upper().center(len(self.world.title) * 3, ' '))
        print()

    # Get player's name and start game
    def setup(self, args):
        self._clear_screen()
        # TODO Uncomment to set player name dynamically
        #choice = input("What is your name? (Leave blank for default) ")
        #if len(choice) > 0:
        #    self.player.set_name(choice)
        self._clear_screen()
        print("Hello, " + self.player.name)
        print("Welcome to " + self.world.title)
        print()
        return ("Instructions", args)

    # TODO Set up instructions state to read helpfile based on command line flag
    def show_instructions(self, args):
        return ("Describe Surrounding", args)
        
    # Describe current world zone
    def describe_surrounding(self, args):
        args = args['current_zone'].describe(args)
        if args['player_dead']:
            return ("Player Died", args)
        return ("Prompt Input", args)

    # Request and parse user input
    # TODO Make better input handling logic
    # TODO create variables for needed substring and lists of keywords of each length to test against
    def prompt(self, args):
        print()
        choice = input("What's next? ")
        self._clear_screen()
        # If nothing was input, try again
        if len(choice) <= 0:
            print("Ummm...")
            return ("Prompt Input", args)
        # If player chooses to exit
        if choice.lower() in ['exit', 'quit', 'q']:
            print("Goodbye, " + self.player.name)
            return ("End Game", args)
        # TODO Display Help
        # TODO Examine Self or item in inventory
        if choice.lower()[:5] == 'check':
            if choice.lower()[6:] in ['self', 'myself', 'me']:
                return ("Examine Self", args)
            elif choice.lower()[6:] in ['bag', 'inventory', 'inv']:
                return ("Check Inventory", args)
            elif choice.lower()[6:] in self.player.inventory:
                print(self.player.inventory[choice.lower()[6:]].name)
                print(self.player.inventory[choice.lower()[6:]].description)
                print()
            else:
                print("Sorry, I don't recognize what you're trying to check")
            return ("Prompt Input", args)
        # Attack Character in Zone
        if choice.lower()[:6] == 'attack':
            if choice.lower()[7:] in args['current_zone'].characters:
                self.player.attack(args['current_zone'].characters[choice.lower()[7:]], args['current_zone'])
            else:
                print("Sorry, that character isn't in this area")
            return ("Prompt Input", args)
        # Check Inventory
        if choice.lower() == 'i' or choice.lower() == 'inventory':
            return ("Check Inventory", args)
        # Equip Item
        if choice.lower()[:5] == 'equip' and choice.lower()[6:] in self.player.inventory:
            try:
                self.player.equip(self.player.inventory[choice.lower()[6:]])
            except TypeError as e:
                print(e.strerror)
                return ("Prompt Input", args)
            print("You equipped the " + choice[6:])
            return ("Prompt Input", args)
        # Input matches exit direction
        if choice.lower() in args['current_zone'].exits:
            args['current_zone'] = args['current_zone'].exits[choice.lower()].destination
            return ("Describe Surrounding", args)
        # Examine Item or Character in Current Zone
        if choice.lower()[:7] in ['examine', 'look at']:
            if choice.lower()[8:] in args['current_zone'].items:
                args['current_zone'].items[choice.lower()[8:]].describe(inventory=False)
            elif choice.lower()[8:] in self.player.inventory:
                self.player.inventory[choice.lower()[8:]].describe(inventory=True)
            elif choice.lower()[8:] in args['current_zone'].characters:
                args['current_zone'].characters[choice.lower()[8:]].describe()
            else:
                print("There doesn't seem to be any of those in this area")
            return ("Prompt Input", args)
        # Look around
        if choice.lower() == 'look' or choice.lower() == 'look around':
            args['current_zone'].look()
            return ("Prompt Input", args)
        # Pickup Item
        if choice.lower()[:4] == 'take':
            if choice.lower()[5:] in args['current_zone'].items:
                self.player.pickup_item(args['current_zone'], args['current_zone'].items[choice.lower()[5:]])
                return ("Prompt Input", args)
            else:
                print("That item doesn't seem to be here")
                return ("Prompt Input", args)
        # Drop Item
        if choice .lower()[:4] == 'drop':
            if choice.lower()[5:] in self.player.inventory:
                self.player.drop_item(args['current_zone'], self.player.inventory[choice.lower()[5:]])
                return ("Prompt Input", args)
            else:
                print("You don't have a " + choice[5:])
                return ("Prompt Input", args)
        # Use Item
        # TODO Maybe use "on" to select a target for item
        if choice .lower()[:3] == 'use':
            if choice.lower()[4:] in self.player.inventory and isinstance(self.player.inventory[choice.lower()[4:]], Potion):
                self.player.inventory[choice.lower()[4:]].use(self.player)
            return ("Prompt Input", args)
        print("Sorry, I don't recognize that command")
        return ("Prompt Input", args)

    # Player chose to quit
    def end_game(self, args):
        print("You quit the game in the " + args['current_zone'].name)

    # Player's body chose for him
    def player_died(self, args):
        print("Sorry " + str(self.player) + ", you died in the " + str(args['current_zone']))
        
if __name__ == "__main__":
    # Initialize Controller and FSM States
    c = controller()
    c.fsm.add_state("Get Player Info", c.setup)
    c.fsm.add_state("Instructions", c.show_instructions)
    c.fsm.add_state("Describe Surrounding", c.describe_surrounding)
    c.fsm.add_state("Prompt Input", c.prompt)
    c.fsm.add_state("Examine Self", c.player.describe)
    c.fsm.add_state("Check Inventory", c.player.check_inventory)
    # TODO Add state for fighting 
    c.fsm.add_state("Fight", f.player.fight)
    c.fsm.add_state("End Game", c.end_game, end_state=True)
    c.fsm.add_state("Player Died", c.player_died, end_state=True)
    # Set initial state and run game with necessary arguments
    c.fsm.set_start("Get Player Info")
    c.fsm.run({ "current_zone": c.start_zone, "player_dead": False, "text_wrap": c.t })
