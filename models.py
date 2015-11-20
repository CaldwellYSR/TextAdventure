import json, sys
import pprint

# Base item class
class Item(object):
    def __init__(self, name="Minor Healing Potion", description="Return some health", heal=True, amount=15, permanent=False):
        self.name = name
        self.description = description
        self.heal = heal
        self.damage = not heal
        self.amount = amount
        self.permanent = permanent

    def __str__(self):
        return self.name

    def describe(self, inventory):
        print self.name + ": " + self.description
        if inventory:
            print "In inventory, type 'use " + self.name.lower() + "' to use it"

    def use(self, target, current_room=None):
        if self.heal:
            print "You heal " + str(self.amount) + " health points to " + str(target)
            target.heal(self.amount, self.permanent)
        else:
            print "You deal " + str(self.amount) + " damage to " + str(target) 
            target.damage(self.amount, self.permanent, current_room)

# TODO Special Item Class for Keys and other Special Story Items or Required Items

# Base Character Class with damage and healing logic
class Character(object):
    def __init__(self, name="Madeleine", inventory={}):
        self.name = name
        self.inventory = inventory
        self.hp = 100
        self.max_hp = 100
        self.alive = True

    def __str__(self):
        return colored(self.name, 'green') if self.alive else colored(self.name, 'red')

    def heal(self, amount, permanent):
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp

    def damage(self, amount, permanent, zone):
        self.hp -= amount
        if self.hp <= 0:
            self.alive = False
            
    def describe(self):
        pass

# Specific type of character that has item inventory helper functions
class Player(Character):
    def set_name(self, name):
        self.name = name

    def pickup_item(self, zone, item=Item()):
        print "You just picked up a " + item.name
        self.inventory[item.name.lower()] = item
        zone.remove_item(item)

    def drop_item(self, zone, item):
        print "You just dropped a " + item.name
        del(self.inventory[item.name.lower()])
        zone.add_item(item)

    def check_inventory(self, args):
        print self.name + "'s Inventory"
        print "=================================================="
        for item in self.inventory:
            print item
        return ("Prompt Input", args)
    
    def describe(self, args):
        print "HP: " + str(self.hp) + "/" + str(self.max_hp)
        print
        return ("Check Inventory", args)

    def damage(self, amount, permanent, zone):
        super(Player, self).damage(amount, permanent, zone)
        if not self.alive:
            args = { "current_zone": zone }
            return ("Player Died", args)
    
# Connects two world zones together
class Connector(object):
    def __init__(self, destination):
        self.destination = destination

# Zone class describes an area in the world, if game_over=True this room will cause an end state
class Zone(object):
    def __init__(self, name="Empty Void", description="Nothing here", game_over=False):
        self.name = name
        self.description = description
        self.game_over = game_over
        self.exits = {}
        self.items = {}
        self.characters = []
    
    def __str__(self):
        return self.name

    # Add exits
    def add_connector(self, connector, direction):
        self.exits[direction] = connector

    # Handling items in this zone
    def add_item(self, item):
        self.items[item.name.lower()] = item

    def remove_item(self, item):
        del(self.items[item.name.lower()])

    # Describe this zone
    def describe(self, args):
        print self.name
        print
        for line in args['text_wrap'].wrap(self.description):
            print line
        if self.game_over:
            args["player_dead"] = True
            print
        return args
    
    # Describe exits, items, and TODO (other characters) in this room
    def look(self):
        print "Exits:"
        print "====================="
        for direction in self.exits:
            print direction + " => " + str(self.exits[direction].destination)
        print
        print "Items:"
        print "====================="
        for id, item in self.items.items():
            print item.name + ': ' + item.description
        print


# World class parses json file to generate the world full of
# zones, connectors, items, TODO add enemy characters
class World(object):
    def __init__(self, f='world.json'):
        self.zones = {}
        # Read JSON File
        json_data = open(f, 'r').read()
        data = json.loads(json_data)
        self.title = data['title']
        tmp = None
        world_zones = data['zones']
        connectors = data['connectors']
        items = data['items']
        # Generate Zones
        for count, z in enumerate(world_zones):
            tmp = Zone(world_zones[z]['title'], world_zones[z]['description'], world_zones[z]['game_over'])
            self._add_zone(str(z), tmp)
            if world_zones[z]['start']:
                self._set_start_zone(z)
        # Generate Connectors
        for c in connectors:
            conn = Connector(self.zones[c['to_id']])
            self.zones[c['from_id']].add_connector(conn, c['direction'])
        # Generate Items
        for item in items:
            i = Item(item['name'], item['description'], item['heal'], item['amount'], item['permanent'])
            self.zones[item['room_id']].add_item(i)
        # TODO Generate other characters

    def __str__(self):
        return self.title

    def _add_zone(self, id, zone):
        self.zones[id] = zone

    def _set_start_zone(self, id):
        self.start_zone = self.zones[id]

    def start(self):
        return self.start_zone
