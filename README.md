# Text Adventure
Text-Based Adventure Game written in Python

# Playing the game:
Playing is simple, run `python main.py` and follow the instructions. If you have your own json file for a different world than my dummy testing world, you can pass it in by running `python main.py -f /path/to/file.json`

# Currently Accepted Commands
`check [me, inventory, inv, bag]` describes your hp and inventory or just your inventory  
`inventory` or `i` also describes your inventory  
`look` or `look around` describes the room you're in plus any items or exits to travel  
`examine` or `look at` + `[item name]` describes an item either in the room or in your inventory  
`[direction]` if the direction matches up with an available exit, this will send you to a new area  
`pickup [item name]` picks up an item if it exists in the current area  
`drop [item name]` drops... you get the picture  
`use [item name]` uses the item.  
`quit exit q` ends the game  

## main.py
This is where most of the input logic resides. As it stands, I am just asking for `raw_input` and then running a bunch of `if elif...` commands based on the input. This might change as this gets bigger. Also initializes the FSM, world, and player

## models.py
This contains all of the classes. The `World` class generates all of the characters, zones, connectors, and items from a json file. 

## world.json
This is a dummy world for now. Eventually this type of file could be use to generate any number of worlds. Use the following format to create your own world file:

##### This format will change as the development continues. Check back often

```json
{
    "title": "World Title",
    "zones": {
        "unique_zone_id": {
            "title": "zone title",
            "description": "zone description",
            "start": bool, 
            "game_over": bool
        }
    },
    "connectors": [
        {
            "to_id": "destination zone id",
            "from_id": "origin zone id",
            "direction": "string user will input to go through this connection"
        }
    ],
    "items": [
        {
            "zone_id": "id of the zone where this item is found",
            "name": "item name",
            "description": "item description",
            "type": "potion"
        }
    ],
    "characters": [
        "zone_id": "id of the zone where this character is found",
        "name": "character name",
        "description": "character description",
        "max_hp": "int",
        "hp": "int",
        "inventory": [
        ]
    ]
}
```

Zones >> Start = (is this the starting zone for this world?)  
Zones >> game_over = (does entering this zone end the game, either via death or winning)  
Items >> type = (`potion` `armor` or `weapon`)  
    Each of these item types come with their own extra arguments. See the appropriate class in `models.py` for a better explanation  
Characters >> inventory = ( a list of `Item`s formatted just like the `items` section above with the extra `equipped` bool )  


### Contacting Me:
I will answer any Issues you open on the site. Outside of that, you can email me at `caldwellysr@gmail.com`

#### Credits:
The finite state machine is not my code. 
I can't remember where I find it but if you recognize it please let me know so I can give proper credit.
