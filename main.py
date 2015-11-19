#!./env/bin/python 

from models import Player, Item, Zone, Connector, World
from fsm import StateMachine
import sys

class controller(object):
    def __init__(self, world=""):
        # Initialize FSM and Player Character
        self.fsm = StateMachine()
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
 
    # Get player's name and start game
    def setup(self, args):
        choice = raw_input("What is your name? (Leave blank default: 'Madeleine') ")
        if len(choice) > 0:
            self.player.set_name(choice)
        print "Hello, " + self.player.name
        print "Welcome to " + self.world.title
        print
        return ("Describe Surrounding", args)

    #TODO Set up instructions state to read helpfile based on command line flag
        
    # Describe current world zone
    def describe_surrounding(self, args):
        args['current_zone'].describe()
        return ("Prompt Input", args)

    # Request and parse user input
    # TODO Make better input handling logic
    def prompt(self, args):
        choice = raw_input("What's next? ")
        # If nothing was input, try again
        if len(choice) <= 0:
            print "Ummm..."
            return ("Prompt Input", args)
        # If player chooses to exit
        if choice.lower() == 'exit' or choice.lower() == 'quit':
            print "Goodbye, " + self.player.name
            return ("End Game", args)
        # Check Inventory
        if choice.lower() == 'i' or choice.lower() == 'inventory':
            return ("Check Inventory", args)
        # Input matches exit direction
        elif choice.lower() in args['current_zone'].exits:
            args['current_zone'] = args['current_zone'].exits[choice.lower()].destination
            return ("Describe Surrounding", args)
        # TODO Pickup Item
        elif choice.lower() == 'look' or choice.lower() == 'look around':
            args['current_zone'].look()
            return ("Prompt Input", args)
        elif choice.lower()[:4] == 'take':
            if choice.lower()[5:] in args['current_zone'].items:
                self.player.pickup_item(args['current_zone'], args['current_zone'].items[choice.lower()[5:]])
                return ("Prompt Input", args)
            else:
                print "That item doesn't seem to be here"
                return ("Prompt Input", args)
        # TODO Use Item
        # TODO Display Help
        else:
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
    c.fsm.add_state("Check Inventory", c.player.check_inventory)
    c.fsm.add_state("Describe Surrounding", c.describe_surrounding)
    c.fsm.add_state("Prompt Input", c.prompt)
    c.fsm.add_state("End Game", c.end_game, end_state=True)
    c.fsm.add_state("Player Died", c.player_died, end_state=True)
    # Set initial state and run game with necessary arguments
    c.fsm.set_start("Get Player Info")
    c.fsm.run({ "current_zone": c.start_zone })
