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
        sz = os.get_terminal_size()
        hr = ""
        for i in range(0, sz[0]):
            hr += '='
        print(colored(hr, 'cyan', attrs=['bold']))
        print(self.world.title.upper().center(sz[0]))
        print(colored(hr, 'cyan', attrs=['bold']))
        print()

    # Get player's name and start game
    def setup(self, args):
        self._clear_screen()
        # TODO Uncomment to set player name dynamically
        #choice = input("What is your name? (Leave blank for default) ")
        #if len(choice) > 0:
        #    self.player.set_name(choice)
        self._clear_screen()
        print("Hello, {name}".format(name=self.player.name))
        print("Welcome to {world}".format(world=self.world.title))
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
    # TODO create keywords dict and test if input
    # is in the keys of the dict, if it is then run the function set in the value of that dict.
    # @see http://stackoverflow.com/questions/9205081/python-is-there-a-way-to-store-a-function-in-a-list-or-dictionary-so-that-when
    def prompt(self, args):
        print()
        choice = input("{prompt}: ".format(prompt=self.world.prompt))
        self._clear_screen()
        # If nothing was input, try again
        if len(choice) <= 0:
            print("Ummm...")
            return ("Prompt Input", args)
        # If player chooses to exit
        if choice.lower() in ['exit', 'quit', 'q']:
            print("Goodbye, {name}".format(name=self.player.name))
            return ("End Game", args)
        # TODO Display Help
        # Input matches exit direction
        if choice.lower() in args['current_zone'].exits:
            if args['current_zone'].exits[choice.lower()].locked:
                print("This door is locked, you can try to unlock it by typing 'unlock {dir}".format(dir=choice.lower()))
                return("Prompt Input", args)
            else:
                args['current_zone'] = args['current_zone'].exits[choice.lower()].destination
            return ("Describe Surrounding", args)
        if choice.lower()[:6] == 'unlock':
            unlocked = False
            if choice.lower()[7:] in args['current_zone'].exits: 
                for key, value in self.player.keys.items():
                    try:
                        unlocked = args['current_zone'].exits[choice.lower()[7:]].unlock(key)
                    except ValueError:
                        pass
            if unlocked:
                args['current_zone'] = args['current_zone'].exits[choice.lower()[7:]].destination
                print("You unlocked the door")
                return ("Describe Surrounding", args)
            else:
                print("It appears you don't have the key")
                return ("Prompt Input")
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
            print("You equipped the {item}".format(item=choice[6:]))
            return ("Prompt Input", args)
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
                art = "an" if choice[0] in ['a','e','i','o','u'] else "a"
                print("You don't have {art} {item}".format(art=art, item=choice[5:]))
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
        print("You quit the game in the {zone}".format(zone=args['current_zone'].name))

    # Player's body chose for him
    def player_died(self, args):
        print("Sorry {player}, you died in the {zone}".format(player=str(self.player), zone=str(args['current_zone'])))
        
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
    #c.fsm.add_state("Fight", c.player.fight)
    c.fsm.add_state("End Game", c.end_game, end_state=True)
    c.fsm.add_state("Player Died", c.player_died, end_state=True)
    # Set initial state and run game with necessary arguments
    c.fsm.set_start("Get Player Info")
    c.fsm.run({ "current_zone": c.start_zone, "player_dead": False, "text_wrap": c.t })
