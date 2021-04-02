#!/usr/bin/env python3

import sys
import os
try:
    from colorama import Fore, Back
except ImportError:
    print("Looks like you don't have the Colorama module installed.")
    print("Run `pip install colorama` to install it")
    exit(1)

SOLVER_ARGS     = ["all",       "bfs",              "dfs",              "dfs-back",                 "keep-left"]
MAKE_COMMANDS   = ["make all",  "make solveBfs",    "make solveDfs",    "make solveDfsBacktrack",   "make solveKeepLeft"]
PROGRAM_NAMES   = ["",          "./solveBfs",       "./solveDfs",       "./solveDfsBacktrack",      "./solveKeepLeft"]

TEST_FILES = ["mazes/big-circle-1.txt", "mazes/big-circle-2.txt", "mazes/small-1.txt", "mazes/small-2.txt"]

OUTPUT_FILE = "output.txt"
ERROR_FILE = "output_err.txt"

C_NORMAL = Fore.WHITE
C_COMMAND = Fore.BLUE
C_ARGS = Fore.MAGENTA
C_ERROR = Fore.RED
C_STRING = Fore.CYAN
C_SUCCESS = Fore.GREEN
C_OUTPUT = Fore.YELLOW

S_TAB = " " * 4

def printUsage():
    print(f"Usage for {C_COMMAND}{sys.argv[0]}{C_NORMAL}:")
    print(f"{S_TAB}{C_COMMAND}{sys.argv[0]} {C_NORMAL}-c [solvers to compile] -t [mazes to test]\n")
    print(f"{S_TAB}Solvers: {C_ARGS}{SOLVER_ARGS}{C_NORMAL}")
    print(f"{S_TAB}Mazes: \"{C_STRING}all{C_NORMAL}\" for all default tests and/or a set of file paths")

def printLines(tab, lines, colour=C_OUTPUT):
    # Print all lines in the file
    for i, line in enumerate(lines):
            print(f"{tab}{str(i + 1).zfill(len(str(len(lines))))}| {colour}{line}{C_NORMAL}", end='')

def runWithOutput(command, indentation, output_notice=False):
    
    # Run command, redirecting output to files
    result = os.system(f"{command} 2> {ERROR_FILE} > {OUTPUT_FILE}")
    
    # Generate indentation
    tab = S_TAB * indentation
    
    # Print error output
    with open(ERROR_FILE) as f:
        lines = f.readlines()
        if len(lines) > 0:
            print(f"{tab}Error output:")
            print(f"{tab}--------------------")
            printLines(tab, lines, colour=C_ERROR)
            print(f"{tab}--------------------")
            print("")
    
    # Print normal output
    with open(OUTPUT_FILE) as f:
        lines = f.readlines()
        if output_notice:
            print(f"{tab}Program output:")
            print(f"{tab}--------------------")
        printLines(tab, lines)
        if output_notice:
            print(f"{tab}--------------------")
    
    os.remove(OUTPUT_FILE)
    os.remove(ERROR_FILE)
    
    return result

def compile(args):
    print(f"Compiling files...")
    
    progs = []
    for arg, command, prog in zip(SOLVER_ARGS, MAKE_COMMANDS, PROGRAM_NAMES):
        if arg in args:
            print(f"{S_TAB}{Fore.CYAN}{arg} {C_NORMAL}->{C_COMMAND} {command}{C_NORMAL}")
            result = runWithOutput(command, 2)
            if result != 0:
                print(f"{S_TAB}{C_ERROR}Compilation failed{C_NORMAL}")
            else:
                if arg == "all":
                    progs += PROGRAM_NAMES[1:]
                else:
                    progs.append(prog)
    
    return progs

def test(args, test_progs):
    print(f"Running tests...")
    
    for prog in test_progs:
        print(f"{S_TAB}Testing {C_COMMAND}{prog}{C_NORMAL}")
        
        arg_num = 0
        while arg_num < len(args):
            tab = S_TAB * 3
            arg = args[arg_num]
            arg_num += 1
            
            print(f"{S_TAB}{S_TAB}{C_ARGS}{arg_num}{C_NORMAL}: Running test {C_COMMAND}{prog} {arg}{C_NORMAL}")
            
            # If we're running all tests
            if arg ==  "all":
                print(f"{tab}Adding {C_STRING}all{C_NORMAL} provided tests\n")
                args += TEST_FILES
                continue
            
            # Run the test
            result = runWithOutput(f"{prog} {arg}", 3, True)
            
            if result != 0:
                print(f"{tab}{C_ERROR}Program exited with error ({result}){C_NORMAL}")
            else:
                print(f"{tab}{C_SUCCESS}Program exited normally{C_NORMAL}")

            print("")
        print("")

if __name__ == "__main__":
    # Extract args
    compile_args = []
    test_args = []
    to_append = None
    for arg in sys.argv:
        if arg in ["-h", "help", "--help"]:
            print("Help:")
            printUsage()
            exit(0)
        if arg == "-c":
            to_append = compile_args
        elif arg == "-t":
            to_append = test_args
        else:
            if to_append is None:
                continue
            else:
                to_append.append(arg)
    
    if len(compile_args) == 0 or len(test_args) == 0:
        print(f"{C_ERROR}Error: incorrect usage{C_NORMAL}")
        printUsage()
        exit(1)
    
    test_progs = compile(compile_args)
    
    test(test_args, test_progs)
