import json, sys
import random as R
from termcolor import colored

# Base item class
class Item(object):
    def __init__(self, name="Minor Healing Potion", description="Return some health"):
        self.name = name
        self.description = description

    def __str__(self):
        return self.name

    def describe(self, inventory):
        print(self.name + ": " + self.description)
        if inventory:
            print(self.name + "Is in your inventory, type 'use " + self.name.lower() + "' to use it")
    
class Potion(Item):
    def __init__(self, name="Minor Healing Potion", description="Return some health", amount=15, permanent=False):
        super().__init__(name, description)
        self.amount = amount
        self.permanent = permanent
        
    def use(self, target, current_room=None):
        print("You heal " + str(self.amount) + " health points to " + str(target))
        target.heal(self.amount, self.permanent)

class Armor(Item):
    def __init__(self, name="Helmet", description="It's a bucket", body_part="head", armor_rating="10"):
        super().__init__(name, description)
        self.body_part = body_part
        self.armor_rating = armor_rating

class Weapon(Item):
    def __init__(self, name="Shiv", description="Sharpened spoon", min_damage=1, max_damage=3):
        super().__init__(name, description)
        self.body_part = "weapon"
        self.min_damage = min_damage
        self.max_damage = max_damage

    def get_damage(self):
        return R.randint(self.min_damage, self.max_damage)

# TODO Special Item Class for Keys and other Special Story Items or Required Items
class Key(Item):
    def __init__(self, name="Key", description="Key with key things", key_id=""):
        super().__init__(name, description)
        self.key_id = key_id

# Base Character Class with damage and healing logic
class Character(object):
    def __init__(self, name="Madeleine", description="Beautiful", hp=100, max_hp=100, base_attack=5, inventory={}):
        self.name = name
        self.description = description
        self.inventory = inventory
        self.hp = 100
        self.max_hp = 100
        self.base_attack = base_attack
        self.alive = True
        self.equipped = {
            "weapon": None,
            "arms": None,
            "head": None,
            "torso": None,
            "legs": None
        }

    def __str__(self):
        return colored(self.name, 'green', attrs=['bold']) if self.alive else colored(self.name, 'red', attrs=['bold'])

    def equip(self, item):
        if not isinstance(item, Armor) and not isinstance(item, Weapon):
            raise TypeError("You can only equip armor and weapons you imbecile")
        if self.equipped[item.body_part] is not None:
            self.inventory[self.equipped[item.body_part].name.lower()] = self.equipped[item.body_part]
        self.equipped[item.body_part] = item
        del(self.inventory[item.name.lower()])

    def heal(self, amount, permanent):
        if permanent:
            self.max_hp += amount
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp

    def attack(self, character, zone):
        damage = self.base_attack
        if isinstance(self.equipped["weapon"], Weapon):
            damage += self.equipped["weapon"].get_damage()
        print("{attacker} attacks {victim} for {damage} damage".format(attacker=self.name, victim=character.name, damage=damage))
        character.take_damage(damage, zone)
        print("{victim} has {health} health left".format(victim=character.name, health=character.hp))

    # TODO Determine if character should fight back, run, or say something
    def take_damage(self, character, amount, zone):
        armor = 0
        for name, value in self.equipped.items():
            if isinstance(value, Armor):
                armor += value.armor_rating
        if amount > armor:
            self.hp = self.hp - (amount - armor)
        if self.hp <= 0:
            self.hp = 0
            self.alive = False
            print ("{victim} is dead and has dropped all items".format(victim=self.name))
            for id, item in self.inventory.items():
                self.drop_item(zone, item)
            for id, item in self.equipped.items():
                try:
                    self.drop_item(zone, item)
                except AttributeError:
                    pass


    def drop_item(self, zone, item):
        if item in self.inventory:
            del(self.inventory[item.name.lower()])
        elif item in self.equipped:
            del(self.equipped[item.name.lower()])

        zone.add_item(item)
         
    def describe(self):
        name = colored(self.name, 'green', attrs=['bold']) if self.alive else colored(self.name, 'red', attrs=['bold'])
        print("{name}: {description}".format(name=name, description=self.description))
        print()
        hp = colored(str(self.hp), 'green', attrs=['bold']) if self.hp >= self.max_hp * 0.4 else colored(str(self.hp), 'red', attrs=['bold'])
        print("HP: {hp}/{max}".format(hp=hp, max=str(self.max_hp)))
        print()
        if self.alive:
            print("Equipped:")
            print("==================================================")
            for key, value in self.equipped.items():
                print(colored("{key}: ".format(key=key.capitalize()), 'cyan', attrs=['bold']) + str(value))
 

# Specific type of character that has item inventory helper functions
class Player(Character):
    def __init__(self):
        self.keys = {}
        return super().__init__(base_attack=10)

    def set_name(self, name):
        self.name = name

    def pickup_item(self, zone, item=Item()):
        art = "an" if item.name[0] in ['a','e','i','o','u'] else "a"
        print("You just picked up {art} {name}".format(art=art, name=item.name))
        self.inventory[item.name.lower()] = item
        zone.remove_item(item)
        if isinstance(item, Key):
            self.keys[item.key_id] = item

    def drop_item(self, zone, item):
        art = "an" if item.name[0] in ['a','e','i','o','u'] else "a"
        print("You just dropped {art} {item}".format(art=art, item=item.name))
        if item in self.inventory:
            del(self.inventory[item.name.lower()])
        elif item in self.equipped:
            del(self.equipped[item.name.lower()])

        zone.add_item(item)
    
    def check_inventory(self, args):
        print()
        print("{player}'s Inventory".format(player=self.name))
        print("==================================================")
        for id, item in self.inventory.items():
            print(item)
        return ("Prompt Input", args)
    
    def describe(self, args):
        hp = colored(str(self.hp), 'green', attrs=['bold']) if self.hp >= self.max_hp * 0.4 else colored(str(self.hp), 'red', attrs=['bold'])
        print("HP: {hp}/{max}".format(hp=hp, max=str(self.max_hp)))
        print()
        print("Equipped:")
        print("==================================================")
        for key, value in self.equipped.items():
            print(colored(key.capitalize() + ": ", 'cyan', attrs=['bold']) + str(value))
        return ("Check Inventory", args)

    # Perform standard take_damage function but then check if you're still alive for state management
    def take_damage(self, amount, permanent, zone):
        super(Player, self).take_damage(amount, zone)
        if not self.alive:
            args = { "current_zone": zone }
            return ("Player Died", args)
    
# Connects two world zones together
class Connector(object):
    def __init__(self, destination, locked=False, key_id=""):
        self.destination = destination
        self.locked = locked
        if self.locked:
            self.key_id = key_id

    def unlock(self, key_id):
        if key_id == self.key_id:
            self.locked = False
            return True
        else:
            raise ValueError("That key isn't right")

# Zone class describes an area in the world, if game_over=True this room will cause an end state
class Zone(object):
    def __init__(self, name="Empty Void", description="Nothing here", game_over=False):
        self.name = name
        self.description = description
        self.game_over = game_over
        self.exits = {}
        self.items = {}
        self.characters = {}
    
    def __str__(self):
        return self.name

    # Add exits
    def add_connector(self, connector, direction):
        self.exits[direction] = connector

    def add_character(self, character):
        self.characters[character.name.lower()] = character

    # Handling items in this zone
    def add_item(self, item):
        self.items[item.name.lower()] = item

    def remove_item(self, item):
        del(self.items[item.name.lower()])

    # Describe this zone
    def describe(self, args):
        print(self.name)
        print()
        for line in args['text_wrap'].wrap(self.description):
            print(line)
        if self.game_over:
            args["player_dead"] = True
            print()
        return args
    
    # Describe exits, items, and TODO (other characters) in this room
    def look(self):
        print("Exits:")
        print("=====================")
        for direction in self.exits:
            print(direction + " => " + str(self.exits[direction].destination))
        print()
        print("Items:")
        print("=====================")
        for id, item in self.items.items():
            print(item)
        print()
        print("Characters:")
        print("=====================")
        for id, char in self.characters.items():
            print(char)



# World class parses json file to generate the world full of
# zones, connectors, items, TODO add enemy characters
class World(object):
    def __init__(self, f='world.json'):
        self.zones = {}
        # Read JSON File
        json_data = open(f, 'r').read()
        data = json.loads(json_data)
        self.title = data['title']
        self.prompt = data['prompt']
        self.instructions = data['instructions']
        # Generate Zones
        self._generate_zones(data['zones'])
        # Generate Connectors
        self._generate_connectors(data['connectors'])
        # Generate Items
        self._generate_items(data['items'])
        # Generate other characters
        self._generate_characters(data['characters'])

    def __str__(self):
        return self.title

    def _add_zone(self, id, zone):
        self.zones[id] = zone

    def _set_start_zone(self, id):
        self.start_zone = self.zones[id]

    def _generate_characters(self, characters):
        for c in characters:
            char = Character(c['name'], c['description'], c['hp'], c['max_hp'], c['base_attack'], c['inventory'])
            self.zones[c['zone_id']].add_character(char)

    def _generate_connectors(self, connectors):
        for c in connectors:
            if 'key_id' in c:
                conn = Connector(self.zones[c['to_id']], True, c['key_id'])
            else:
                conn = Connector(self.zones[c['to_id']])
            self.zones[c['from_id']].add_connector(conn, c['direction'])

    def _generate_items(self, items):
        for item in items:
            if item['type'] == 'potion':
                i = Potion(item['name'], item['description'], item['amount'], item['permanent'])
            elif item['type'] == 'armor':
                i = Armor(item['name'], item['description'], item['body_part'], item['armor_rating'])
            elif item['type'] == 'weapon':
                i = Weapon(item['name'], item['description'], item['min_damage'], item['max_damage'])
            elif item['type'] == 'key':
                i = Key(item['name'], item['description'], item['key_id'])
            self.zones[item['zone_id']].add_item(i)

    def _generate_zones(self, world_zones):
        for count, z in enumerate(world_zones):
            tmp = Zone(world_zones[z]['title'], world_zones[z]['description'], world_zones[z]['game_over'])
            self._add_zone(str(z), tmp)
            if world_zones[z]['start']:
                self._set_start_zone(z)

    def print_instructions(self, args):
        for i in self.instructions:
            print(i)
        return ("Describe Surrounding", args)

    def start(self):
        return self.start_zone
