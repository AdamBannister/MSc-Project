def TextParser(filename):
    lst = []
    with open(filename) as a:
        b = a.readlines()
        c = b[5001].split()
    for x in c:
        x = re.sub('[^0123456789.]+', '', x)
        #print x
        lst.append(float(x))
    return(lst)

def LineCompiler(linelist, output_filename):
    output = open(output_filename, "w+")
    for i in range(len(linelist)):
        outputstr = ""
        element = linelist[i]
        for number in element:
            appendstr = str(number).strip() + " "
            outputstr = outputstr + appendstr
        outputstr = outputstr + "\n"
        output.write(outputstr)
    output.close()
