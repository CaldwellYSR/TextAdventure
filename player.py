#!./env/bin/python

from Item import Item

class Player(object):
    def __init__(self, name = "Madeleine"):
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
