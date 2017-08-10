import sys
import re

def main(args):
    inputfilename = str(args[0])
    desired_state = str(args[1])
    try:
        outputfilename = str(args[2])
    except IndexError:
        outputfilename = desired_state + "_" + inputfilename
    linelst = []
    statestr = str(desired_state)
    print statestr
    with open(inputfilename, "r+") as ipf:
        with open(outputfilename, "w+") as opf:
            for n in range(len(ipf.readlines())):
                if n == 0:
                    ipf.seek(0)
                    ipf.readline()
                else:
                    line = str(ipf.readline())
                    if statestr in line:
                        linelst.append(line)
            for i in range(len(linelst)):
                opf.write(linelst[i])

if (__name__ == '__main__'):
    main(sys.argv[1:])