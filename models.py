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

    def check_inventory(self, args):
        print self.name + "'s Inventory"
        print "=================================================="
        for item in self.inventory:
            print item
        return ("Describe Surrounding", args)

    def pickup_item(self, item=Item()):
        self.inventory.append(item)

class Room(object):
    def __init__(self, name="Empty Void"):
        self.name = name
