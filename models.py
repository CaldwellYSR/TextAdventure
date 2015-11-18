class Item(object):
    def __init__(self, name="Bag of Holding"):
        self.name = name

    def __str__(self):
        return self.name

class Player(object):
    def __init__(self, name="Madeleine"):
        self.name = name
        self.inventory = []

    def __str__(self):
        return self.name

    def pickup_item(self, item=Item()):
        self.inventory.append(item)

    def set_name(self, name):
        self.name = name

    def check_inventory(self, args):
        print self.name + "'s Inventory"
        print "=================================================="
        for item in self.inventory:
            print item
        return ("Describe Surrounding", args)

class Connector(object):
    def __init__(self, destination):
        self.destination = destination

class Zone(object):
    def __init__(self, name="Empty Void", game_over=False):
        self.name = name
        self.game_over = game_over
        self.exits = {}
    
    def __str__(self):
        return self.name

    def add_connector(self, connector, direction):
        self.exits[direction] = connector
