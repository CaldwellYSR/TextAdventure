#!./env/bin/python 

from models import Player, Item, Zone, Connector, World
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
                print "You didn't include a file"
                sys.exit(0)
            self.world = World(f)
        else:
            self.world = World()
        # Set initial "Zone" to start character in
        self.start_zone = self.world.start()
 
    def _clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print
        print self.world.title.upper().center(len(self.world.title) * 3, ' ')
        print

    # Get player's name and start game
    def setup(self, args):
        self._clear_screen()
        # TODO Uncomment to set player name dynamically
        #choice = raw_input("What is your name? (Leave blank for default) ")
        #if len(choice) > 0:
        #    self.player.set_name(choice)
        self._clear_screen()
        print "Hello, " + self.player.name
        print "Welcome to " + self.world.title
        print
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
    def prompt(self, args):
        print
        choice = raw_input("What's next? ")
        # If nothing was input, try again
        if len(choice) <= 0:
            self._clear_screen()
            print "Ummm..."
            return ("Prompt Input", args)
        # If player chooses to exit
        if choice.lower() == 'exit' or choice.lower() == 'quit':
            self._clear_screen()
            print "Goodbye, " + self.player.name
            return ("End Game", args)
        # TODO Display Help
        # TODO Examine Self
        if choice.lower()[:5] == 'check':
            if choice.lower()[6:] in ['self', 'myself', 'me']:
                self._clear_screen()
                return ("Examine Self", args)
            elif choice.lower()[6:] in ['bag', 'inventory', 'inv']:
                self._clear_screen()
                return ("Check Inventory", args)
            elif choice.lower()[6:] in self.player.inventory:
                self._clear_screen()
                print self.player.inventory[choice.lower()[6:]].name
                print self.player.inventory[choice.lower()[6:]].description
                print
            else:
                self._clear_screen()
                print "Sorry, I don't recognize what you're trying to check"
            return ("Prompt Input", args)
        # Check Inventory
        if choice.lower() == 'i' or choice.lower() == 'inventory':
            self._clear_screen()
            return ("Check Inventory", args)
        # Input matches exit direction
        elif choice.lower() in args['current_zone'].exits:
            self._clear_screen()
            args['current_zone'] = args['current_zone'].exits[choice.lower()].destination
            return ("Describe Surrounding", args)
        # Examine Item in Zone
        elif choice.lower()[:7] in ['examine', 'look at']:
            if choice.lower()[8:] in args['current_zone'].items:
                self._clear_screen()
                args['current_zone'].items[choice.lower()[8:]].describe(inventory=False)
            elif choice.lower()[8:] in self.player.inventory:
                self._clear_screen()
                self.player.inventory[choice.lower()[8:]].describe(inventory=True)
            else:
                self._clear_screen()
                print "That item doesn't seem to be here"
            return ("Prompt Input", args)
        # Pickup Item
        elif choice.lower() == 'look' or choice.lower() == 'look around':
            self._clear_screen()
            args['current_zone'].look()
            return ("Prompt Input", args)
        elif choice.lower()[:4] == 'take':
            if choice.lower()[5:] in args['current_zone'].items:
                self._clear_screen()
                self.player.pickup_item(args['current_zone'], args['current_zone'].items[choice.lower()[5:]])
                return ("Prompt Input", args)
            else:
                self._clear_screen()
                print "That item doesn't seem to be here"
                return ("Prompt Input", args)
        # Drop Item
        elif choice .lower()[:4] == 'drop':
            if choice.lower()[5:] in self.player.inventory:
                self._clear_screen()
                self.player.drop_item(args['current_zone'], self.player.inventory[choice.lower()[5:]])
                return ("Prompt Input", args)
            else:
                self._clear_screen()
                print "You don't have a " + choice[5:]
                return ("Prompt Input", args)
        # Use Item
        # TODO Maybe use "on" to select a target for item
        elif choice .lower()[:3] == 'use':
            if choice.lower()[4:] in self.player.inventory:
                if self.player.inventory[choice.lower()[4:]].heal:
                    self._clear_screen()
                    self.player.inventory[choice.lower()[4:]].use(self.player)
                else:
                    self._clear_screen()
                    self.player.inventory[choice.lower()[4:]].use(args['current_zone'].characters.pop(), args['current_room'])
                return ("Prompt Input", args)
        else:
            self._clear_screen()
            print "Sorry, I don't recognize that command"
            return ("Prompt Input", args)

    # Player chose to quit
    def end_game(self, args):
        print "You quit the game in the " + args['current_zone'].name

    # Player's body chose for him
    def player_died(self, args):
        print "Sorry " + str(self.player) + ", you died in the " + str(args['current_zone'])
        
if __name__ == "__main__":
    # Initialize Controller and FSM States
    c = controller()
    c.fsm.add_state("Get Player Info", c.setup)
    c.fsm.add_state("Instructions", c.show_instructions)
    c.fsm.add_state("Describe Surrounding", c.describe_surrounding)
    c.fsm.add_state("Prompt Input", c.prompt)
    c.fsm.add_state("Examine Self", c.player.describe)
    c.fsm.add_state("Check Inventory", c.player.check_inventory)
    c.fsm.add_state("End Game", c.end_game, end_state=True)
    c.fsm.add_state("Player Died", c.player_died, end_state=True)
    # Set initial state and run game with necessary arguments
    c.fsm.set_start("Get Player Info")
    c.fsm.run({ "current_zone": c.start_zone, "player_dead": False, "text_wrap": c.t })
