#!./env/bin/python

class Item(object):
    def __init__(self, name="Bag of Holding"):
        self.name = name

    def __str__(self):
        return self.name
