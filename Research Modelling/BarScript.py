import matplotlib.pyplot as plt
import sys
import numpy as np

def main(inputfile, iterationnum):
    inputlst = []
    outputlst = []
    with open(inputfile, "r+") as ipf:
        for x in range(len(ipf.readlines())-1):
            if x == 0:
                ipf.seek(0)
                ipf.readline()
            inputline = ipf.readline()
            if iterationnum > 9:
                n = 1
            else:
                n = 0
            iterstr = inputline[:1+n]
            iterint = int(iterstr)
            if iterint == int(iterationnum):
                iterline = inputline.strip(",")
                iterline = iterline.strip()
                inputstr = iterline[1+n:5+n]
                revline = iterline[::-1]
                iterstr = ""
                outputstr = ""
                for y in range(len(revline)):
                    char = revline[y]
                    if char != " ":
                        iterstr = iterstr + str(char)
                    else:
                        outputstr = outputstr + iterstr[::-1]
                        break
                inputlst.append(inputstr)
                outputlst.append(outputstr)
    n = len(inputlst)
    ind = np.arange(n)
    width = 0.1
    fig, ax = plt.subplots()
    rects = ax.bar(ind, outputlst)
    ax.set_ylabel("Output concentration")
    ax.set_xlabel("Inducer input state")
    ax.set_xticks(ind + width / 3)
    ax.set_xticklabels(tuple(inputlst))
    fig.set_size_inches(6, 4)
    plt.show()

if (__name__ == '__main__'):
    main(sys.argv[1], sys.argv[2])
