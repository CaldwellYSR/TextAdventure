#!./env/bin/python

#############################################################
# Simple Finite State Machine                               #
#############################################################
# To use, initialize a new instance of StateMachine         #
# then use the `add_state` method to pair functions to      #
# string identifiers.                                       #
#                                                           #
# Make sure to set a starting state with `set_start`        #
#                                                           #
# Finally, `run` the FSM to loop through your states.       #
#                                                           #
# Each state function should return a tuple with a string   #
# Identifying the next state and a dictionary with any      #
# arguments you need to pass along                          #
#############################################################

class StateMachine:
    def __init__(self):
        self.handlers = {}
        self.startState = None
        self.endStates = []

    def add_state(self, name, handler, end_state=0):
        name = name.upper()
        self.handlers[name] = handler
        if end_state:
            self.endStates.append(name)

    def set_start(self, name):
        self.startState = name.upper()

    def run(self, args):
        try:
            handler = self.handlers[self.startState]
        except:
            raise InitializationError("must call .set_start() before .run()")
        if not self.endStates:
            raise  InitializationError("at least one state must be an end_state")
    
        while True:
            (newState, args) = handler(args)
            if newState.upper() in self.endStates:
                handler = self.handlers[newState.upper()]  
                handler(args)
                break 
            else:
                handler = self.handlers[newState.upper()]  
