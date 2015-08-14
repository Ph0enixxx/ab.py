#!/usr/bin/python

import argparse

# control the connectins
class connections(object):
    pass

# the cmd input argument.
class params(object):
    def __init__(self):
        self.recverrok=True
    
def test():
    pass

def arguments_parse():
    
    print(args)
    return args

def validate_arguments(args):
    """
    valide the arguments
    return args is 
    """
    return (True, None)

def main():
    args = arguments_parse()
    valid, cause = validate_arguments(args)
    if not valid:
        print(cause)
        return 
    

if __name__ == '__main__':
    main() 


