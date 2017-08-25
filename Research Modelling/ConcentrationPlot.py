#!/usr/bin/python

# Author: Adam Bannister, Newcastle University.

import matplotlib.pyplot as plt
import sys

def main(args):
    # Empty lists defined for later appending.
    """Plots input/output concentration curve of a parsed file from ModelScript4.py. Arguments:
    'filename' is name of the parsed .txt file.
    'inputname' is the name of the input/inducer species in the model results.
    'outputname' is the name of the output/reporter in the mode results.
    'logxYN' is an optional argument which specifies whether the X axis scale should be logarithmic. Default N (no)."""
    inputlst = []
    outputlst = []
    filename = str(args[0])
    inputname = str(args[1])
    outputname = str(args[2])
    try:
        logxYN = str(args[3])
    except IndexError:
        logxYN = "N"

    inputlocation = 0
    outputlocation = 0

    with open(filename, "r+") as ipf:
        for n in range(len(ipf.readlines())-1):
            if n == 0:
                ipf.seek(0)
                checkline = ipf.readline()
                checkline = checkline.strip()
                checkline = checkline.replace(",","")
                checkline = checkline.split()
                print checkline
                for i in range(len(checkline)):
                    if str(checkline[i]) == inputname:
                        inputlocation = inputlocation + i
                    elif str(checkline[i]) == outputname:
                        outputlocation = outputlocation + i
            inputline = ipf.readline()
            iterline = inputline.strip(",")
            iterline = iterline.strip()
            splitline = iterline.split()
            inputstr = splitline[inputlocation+1]
            outputstr = splitline[outputlocation+1]
            inputlst.append(inputstr)
            outputlst.append(outputstr)
    fig, ax = plt.subplots()
    ax.set_xlabel("Input concentration (mmol/ml)")
    ax.set_ylabel("Output concentration (mmol/ml)")
    plt.gca().ticklabel_format(style='sci', scilimits=(0, 1), axis='y')
    if logxYN == "Y":
        plt.xscale("log")
    plt.plot(inputlst, outputlst)
    plt.show()
if (__name__ == '__main__'):
    main(sys.argv[1:])