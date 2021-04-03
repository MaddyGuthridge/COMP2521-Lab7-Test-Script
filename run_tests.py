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

OUTPUT_CUTOFF = 50

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

CLEAR_SCREEN_ANSI = "[1;1H[2J"

def printUsage():
    print(f"Usage for {C_COMMAND}{sys.argv[0]}{C_NORMAL}:")
    print(f"{S_TAB}{C_COMMAND}{sys.argv[0]} {C_NORMAL} [{C_ARGS}-s{C_NORMAL}] {C_ARGS}-c{C_NORMAL} [solvers to compile]"
          f" {C_ARGS}-t{C_NORMAL} [mazes to test] {C_ARGS}-a{C_NORMAL} [extra args for tests]\n")
    print(f"{S_TAB}{C_ARGS}-s{C_NORMAL}: Don't display program output while running (will still display after)")
    print(f"{S_TAB}Solvers: {C_ARGS}{SOLVER_ARGS}{C_NORMAL}")
    print(f"{S_TAB}Mazes: \"{C_STRING}all{C_NORMAL}\" for all default tests and/or a set of file paths")
    print(f"{S_TAB}Extra args for tests: these will be passed onto each tested program for every test")

def printLines(tab, lines, colour=C_OUTPUT, print_last=-1):
    # Print all lines in the file (unless print_last is specified, in which case
    # print only the last n lines)
    
    fill_amount = len(str(len(lines)))
    
    extended_line_filler = f"\n{tab}{' ' * fill_amount}{C_NORMAL}| {colour}"
    
    if len(lines) < print_last:
        print_last = -1

    count_start = 1
    if print_last != -1:
        count_start += len(lines) - print_last
    
    if print_last != -1:
        lines = lines[-print_last: ]
    
    for i, line in enumerate(lines):
            if CLEAR_SCREEN_ANSI in line:
                line = line.replace(CLEAR_SCREEN_ANSI, f"{extended_line_filler}[Clear console]{extended_line_filler}")
            print(f"{tab}{str(i + count_start).rjust(fill_amount)}| {colour}{line}{C_NORMAL}", end='')

def runWithOutput(command, indentation, output_notice=False, silent_run=False):
    if not silent_run:
        # Open a new terminal layer
        # Thanks, https://stackoverflow.com/a/11024208/6335363
        os.system("tput smcup")
        # Run command, redirecting output to files
        result = os.system(f"stdbuf --output=L {command} 2> {ERROR_FILE} | tee {OUTPUT_FILE}")
        # Close that terminal layer
        os.system("tput rmcup")
    else:
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
        printLines(tab, lines, print_last=OUTPUT_CUTOFF)
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
            result = runWithOutput(command, 2, silent_run=False)
            if result != 0:
                print(f"{S_TAB}{C_ERROR}Compilation failed{C_NORMAL}")
            else:
                if arg == "all":
                    progs += PROGRAM_NAMES[1:]
                else:
                    progs.append(prog)
    
    return progs

def test(args, test_progs, additional_args, silent):
    print(f"Running tests...")
    args_to_run = args.copy()
    
    for prog in test_progs:
        print(f"{S_TAB}Testing {C_COMMAND}{prog}{C_NORMAL}")
        
        arg_num = 0
        while arg_num < len(args_to_run):
            tab = S_TAB * 3
            arg = args_to_run[arg_num]
            arg_num += 1
            
            print(f"{S_TAB}{S_TAB}{C_ARGS}{arg_num}{C_NORMAL}: Running test {C_COMMAND}{prog} {arg}{C_NORMAL}")
            
            # If we're running all tests
            if arg ==  "all":
                print(f"{tab}Adding {C_STRING}all{C_NORMAL} provided tests\n")
                args_to_run = args + TEST_FILES
                continue
            
            # Run the test
            result = runWithOutput(f"{prog} {arg} {additional_args}", 3, True, silent)
            
            if result != 0:
                print(f"{tab}{C_ERROR}Program exited with error ({result}){C_NORMAL}")
            else:
                print(f"{tab}{C_SUCCESS}Program exited normally{C_NORMAL}")

            print("")
        print("")

if __name__ == "__main__":
    
    # Clear console (since otherwise it's easy to accidentally scroll weird)
    print(CLEAR_SCREEN_ANSI)
    
    # Extract args
    compile_args = []
    test_args = []
    additional_args = []
    to_append = None
    silent = False
    for arg in sys.argv:
        if arg in ["-h", "help", "--help"]:
            print("Help:")
            printUsage()
            exit(0)
        if arg == "-c":
            to_append = compile_args
        elif arg == "-t":
            to_append = test_args
        elif arg == "-a":
            to_append = additional_args
        elif arg == "-s":
            silent = True
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
    
    test(test_args, test_progs, " ".join(additional_args), silent)

    print(f"{C_SUCCESS}All tests complete!{C_NORMAL}")
    print("")
