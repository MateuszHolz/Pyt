#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import traceback
from TScript import *

class MockEnvironment(TScriptEnvironment):
    def __init__(self):
        self.functions = {
            "cmd1" : lambda: self.getContentOfFile("/etc/fstab"),
            "cmd2" : lambda: self.getContentOfFile("/etc/mtab"),
            "cmd3" : lambda: self.getContentOfFile("/etc/shells"),
            "cmd4" : lambda: self.getContentOfFile("/etc/nsswitch.conf"),
            "cmd5" : lambda: self.getContentOfFile("/etc/bash.bashrc"),
            "cmd6" : lambda: self.getContentOfFile("/etc/mc/sfs.ini"),
        }

    def getContentOfFile(self, name):
        with open(name, "r") as f:
            return f.readlines()

    def execFunction(self, command, args, line):
        return self.functions[command]()

def testFilters(env):
    decoration = 50 * "="
    commands = [
        "cmd1",
        "cmd1 | filter Cygwin",
        "cmd1 | grep '[cC]ygwin'",
        "cmd3",
        "cmd3 | head",
        "cmd3 | head -n 3",
        "cmd3 | tail",
        "cmd3 | tail -n", # Wrong syntax case
        "cmd3 | tail -n 1",
        "cmd3 | wc -l",
        "cmd3 | head | wc -l",
        "cmd3 | head | wc",
        "cmd3 | sort",
        "cmd4",
        "cmd4 | grep -o '[a-z_]+:'",
        "cmd4 | grep -v '[a-z_]+:'",
    ]

    for cmd in commands:
        print(decoration)
        print("Command: '{0}'; Output:".format(cmd))
        print(decoration)
        instruction = None
        result = None

        try:
            instruction = TScriptCommandParser.build(cmd)
            result = instruction.exec(env)
            for line in result:
                print(line.rstrip())
        except Exception as e:
            print(e)
            print(traceback.format_exc())

def testScriptParser(env):
    testScript = r"""
# vim: set syntax=sh:
#
cmd1 a1 a2 a3
cmd2 a b

cmd3 a

# Test komentarza:
function f {
    # Komentarz:
    cmd4 | grep 'test'
    cmd5

    cmd6 | filter string
}

function mocz {
    cmd1 z w
    cmd2 x y
}
    """
    parser = TScriptScopeBuilder()
    result = parser.parse(testScript)

    parser.printData()

def main():
    env = MockEnvironment()
    testFilters(env)
    # testScriptParser(env)
 
if __name__ == "__main__":
    main()
