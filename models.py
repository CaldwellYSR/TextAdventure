import json, sys
import pprint

class Item(object):
    def __init__(self, name="Minor Healing Potion", description="Return some health", heal=True, amount=15, permanent=False):
        self.name = name
        self.description = description
        self.heal = heal
        self.damage = not heal
        self.permanent = permanent

    def __str__(self):
        return self.name

    def use(self, args):
        if self.heal:
            args['target'].heal(self.amount, self.permanent, args)
        else:
            args['target'].damage(self.amount, self.permanent, args)
        del(args['target'])
        return ("Prompt Input", args)

class Character(object):
    def __init__(self, name="Madeleine", inventory=[]):
        self.name = name
        self.inventory = inventory
        self.hp = 100
        self.max_hp = 100

    def __str__(self):
        return self.name

    def heal(self, amount, permanent, args):
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp

    def damage(self, amount, permanent, args):
        self.hp -= amount
        if self.hp <= 0:
            return ("Player Died", args)

class Player(Character):
    def set_name(self, name):
        self.name = name

    def pickup_item(self, zone, item=Item()):
        print "You just picked up a " + item.name
        self.inventory.append(item)
        zone.remove_item(item)

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
    def __init__(self, name="Empty Void", description="Nothing here", game_over=False):
        self.name = name
        self.description = description
        self.game_over = game_over
        self.exits = {}
        self.items = {}
    
    def __str__(self):
        return self.name

    def add_connector(self, connector, direction):
        self.exits[direction] = connector

    def add_item(self, item):
        self.items[item.name.lower()] = item

    def remove_item(self, item):
        del(self.items[item.name.lower()])

    # Describe this zone
    def describe(self):
        print self.name
        print
        print self.description
        if self.game_over:
            return ("Player Died", args)
    
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
