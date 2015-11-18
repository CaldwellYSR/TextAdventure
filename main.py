#!./env/bin/python

from models import Player, Item, Room
from fsm import StateMachine

class controller(object):
    def __init__(self):
        self.fsm = StateMachine()
        item1 = Item()
        self.player = Player("Matthew")
        self.player.pickup_item(item1)
        room1 = Room("Grand Entrance")
        self.start_room = room1

    def describe_surrounding(self, current_room):
        print current_room.name
        room2 = Room("Grand Hallway")
        current_room = room2
        return ("Prompt Input", current_room)

    def prompt(self, current_room):
        choice = raw_input("What's next? ")
        if len(choice) <= 0:
            print "Ummm..."
            return ("Prompt Input", current_room)
        if choice.lower() == 'i' or choice.lower() == 'inventory':
            return ("Check Inventory", current_room)
        else:
            return ("End Game", current_room)

    def end_game(self, current_room):
        pass
        
if __name__ == "__main__":
    c = controller()
    c.fsm.add_state("Check Inventory", c.player.check_inventory)
    c.fsm.add_state("Describe Surrounding", c.describe_surrounding)
    c.fsm.add_state("Prompt Input", c.prompt)
    c.fsm.add_state("End Game", c.end_game, end_state=True)
    c.fsm.set_start("Describe Surrounding")
    c.fsm.run(c.start_room)
