#!./env/bin/python

from player import Player
from Item import Item
from fsm import StateMachine

class controller(object):
    def __init__(self):
        self.fsm = StateMachine()
        item1 = Item()
        self.player = Player("Matthew")
        self.player.pickup_item(item1)

    def describe_surrounding(self, args):
        print "It's raining"
        return ("Prompt Input", args)

    def prompt(self, args):
        while True:
            choice = raw_input("What's next? ")
            if len(choice) > 0:
                break;
        if choice.lower() == 'i' or choice.lower() == 'inventory':
            return ("Check Inventory", args)
        else:
            return ("End Game", args)

    def end_game(self, args):
        pass
        
if __name__ == "__main__":
    c = controller()
    c.fsm.add_state("Check Inventory", c.player.check_inventory)
    c.fsm.add_state("Describe Surrounding", c.describe_surrounding)
    c.fsm.add_state("Prompt Input", c.prompt)
    c.fsm.add_state("End Game", c.end_game, end_state=True)
    c.fsm.set_start("Describe Surrounding")
    c.fsm.run("")
