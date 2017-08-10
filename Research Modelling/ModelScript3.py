from COPASI import *
import sys
import itertools
import re


def TextParser(filename, targetline):
    """TextParser function. 2 arguments: filename of COPASI output and target line to parse. Output: list of
    lines with trailing punctuation removed.."""
    lst = []
    with open(filename) as a:
        b = a.readlines()
        c = b[targetline].split()
    for x in c:
        # Removes commas from COPASI text output.
        x = re.sub('[^0123456789.]+', '', x)
        #print x
        lst.append(float(x))
    return(lst)

def LineCompiler(linelist, output_filename):
    output = open(output_filename, "a+")
    for i in range(len(linelist)):
        outputstr = ""
        element = linelist[i]
        for number in element:
            appendstr = str(number).strip() + " "
            outputstr = outputstr + appendstr
        outputstr = outputstr + "\n"
        output.write(outputstr)
    output.close()

def main(args):
    """Function to generate a range of COPASI models with three values for input concentrations.
    Arguments: 'filename' is a string pointing to the model file in XML (SBML) format in the local directory.
    'minimum_concentration' is the minimum concentrentration of input A.
    'max_concentration' is the maximum concentration of input A.
    'iterations' is the number of models generated between the minimum and maximum concentrations specified. Default=10.
    'duration' is the time course duration in seconds. Step count = duration in seconds. Default = 5000.
    'trinaryratio' is the ratio of the three-valued logic state intermediate to the max ('1' to '2' using 012 notation).
    'Bratio' is the ratio of input B to input A, e.g. a value of 2 will give twice the amount of B relative to A.
    """
    # 'args' is fed to the main function as a tuple. Defining variables & ensuring type is correct.
    filename = str(args[0])
    min_concentration = float(args[1])
    max_concentration = float(args[2])

    try:
        iterations = int(args[3])
    except IndexError:
        iterations = 10

    try:
        duration = float(args[4])
    except IndexError:
        duration = 5000

    try:
        trinaryratio = float(args[4])
    except IndexError:
        trinaryratio = 2.0

    try:
        Bratio = float(args[5])
    except IndexError:
        Bratio = 1.0

    try:
        assert isinstance(filename, str)
        assert isinstance(min_concentration, (int, float))
        assert isinstance(max_concentration, (int, float))
        assert isinstance(iterations, int)
        assert isinstance(trinaryratio, (int, float))
        assert isinstance(Bratio, (int, float))
    except TypeError:
        print("Incorrect type for argument(s). Arguments: filename as string, min_concentration as integer \
                or float, max_concentration as integer or float. Optional: iterations as integer (default 10),\
                trinaryratio as integer or float (default 2), Bratio as integer or float (default 1).")

    # Housekeeping.
    assert CCopasiRootContainer.getRoot() != None
    assert CCopasiRootContainer.getDatamodelList().size() == 0
    dataModel = CCopasiRootContainer.addDatamodel()
    # Importing from file. SBML  format - functionality here could be expanded for .cps files.
    dataModel.importSBML(filename)
    model = dataModel.getModel()
    # Defining a vector of changed objects, which can then be pushed back onto the higher-level classes.
    changedObjects = ObjectStdVector()
    # Creating a report to display/output timecourse results. Code here taken from Python-COPASI package Example1.py.
    reports = dataModel.getReportDefinitionList()
    report = reports.createReportDefinition("Report", "Time course output")
    report.setTaskType(CTaskEnum.timeCourse)
    report.setIsTable(False)
    report.setSeparator(CCopasiReportSeparator(", "))
    header = report.getHeaderAddr()
    body = report.getBodyAddr()
    body.push_back(CRegisteredObjectName(
        CCopasiObjectName(dataModel.getModel().getCN().getString() + ",Reference=Time").getString()))
    body.push_back(CRegisteredObjectName(report.getSeparator().getCN().getString()))
    header.push_back(CRegisteredObjectName(CCopasiStaticString("time").getCN().getString()))
    header.push_back(CRegisteredObjectName(report.getSeparator().getCN().getString()))
    iMax = model.getMetabolites().size()
    parsedlines = []
    for i in range(0, iMax):
        metab = model.getMetabolite(i)
        assert metab != None
        body.push_back(
            CRegisteredObjectName(metab.getObject(CCopasiObjectName("Reference=Concentration")).getCN().getString()))
        header.push_back(CRegisteredObjectName(CCopasiStaticString(metab.getSBMLId()).getCN().getString()))
        if (i != iMax - 1):
            body.push_back(CRegisteredObjectName(report.getSeparator().getCN().getString()))
            header.push_back(CRegisteredObjectName(report.getSeparator().getCN().getString()))

    # Defining directory path for output filename (used by script) and dump filename.
    outputfilename = filename[:-4] + "_output.txt"
    dumpfilename = "Dump_" + outputfilename
    with open(dumpfilename, "w+") as dfn:
        dfn.truncate(0)

    parsedfilename = "Parsed_" + outputfilename
    with open(parsedfilename, "w+") as pfn:
        pfn.truncate(0)

    # Defining a list for the iterations of the model to be generated.
    # iterationlist = [x+1 for x in range(iterations)
    for n in range(iterations):
        # Parameter definitions: defining the trinary input values, here labelled as 0, 1 and 2.
        iteration_increment = (float(n+1)/float(iterations)) * (float(max_concentration) - float(min_concentration))
        input_0_A = min_concentration
        input_0_B = input_0_A * Bratio
        input_1_A = min_concentration + iteration_increment/trinaryratio
        input_1_B = input_1_A * Bratio
        input_2_A = min_concentration + iteration_increment
        input_2_B = input_2_A * Bratio
        # Defining metabolite variables.
        inducer_A = model.getMetabolite("Inducer_A")
        inducer_B = model.getMetabolite("Inducer_B")
        # For each iteration, need to do runs to cover 0, 1 and 2 for each input. Tuples include strings to denote
        # the value of each of the inputs.
        A_vec = [(input_0_A, "A0"), (input_1_A, "A1"), (input_2_A, "A2")]
        B_vec = [(input_0_B, "B0"), (input_1_B, "B1"), (input_2_B, "B2")]
        combinations = list(itertools.product(A_vec, B_vec))

        for j in range(len(combinations)):
            entry = combinations[j]
            A_conc = (entry[0])[0]
            B_conc = (entry[1])[0]
            inducer_A.setInitialConcentration(A_conc)
            inducer_B.setInitialConcentration(B_conc)

            # Push back the changes to higher-level classes.
            object = inducer_A.getInitialConcentrationReference()
            changedObjects.push_back(object)
            model.updateInitialValues(changedObjects)
            object = inducer_B.getInitialConcentrationReference()
            changedObjects.push_back(object)
            model.updateInitialValues(changedObjects)
            model.compileIfNecessary()
            # Output name variable assigned as a string which gives the states of the two inputs.
            outputnamevar = ( (entry[0])[1] + (entry[1])[1] )
            # outputfilename = filename[:-4] + " iteration " + str(n+1) + " " + outputnamevar + ".txt"

            # Running a time course. Code adapted from Python-COPASI package example scripts
            # Time course with one step per second. Method is deterministic (LSODA).
            trajectoryTask = dataModel.getTask("Time-Course")
            trajectoryTask.setMethodType(CTaskEnum.deterministic)
            trajectoryTask.getProblem().setModel(dataModel.getModel())
            trajectoryTask.setScheduled(True)
            trajectoryTask.getReport().setReportDefinition(report)
            trajectoryTask.getReport().setTarget(outputfilename)
            trajectoryTask.getReport().setAppend(False)
            problem = trajectoryTask.getProblem()
            problem.setStepNumber(duration)
            dataModel.getModel().setInitialTime(0.0)
            problem.setDuration(duration)
            problem.setTimeSeriesRequested(True)
            # LSODA parameters being set are the same as the default within the COPASI UI.
            method = trajectoryTask.getMethod()
            parameter = method.getParameter("Absolute Tolerance")
            assert parameter != None
            assert parameter.getType() == CCopasiParameter.UDOUBLE
            parameter.setValue(1.0e-12)
            result = True
            try:
                result = trajectoryTask.process(True)
            except:
                sys.stderr.write("Error. Running the time course simulation failed.\n")
                if CCopasiMessage.size() > 0:
                    sys.stderr.write(CCopasiMessage.getAllMessageText(True))
                return 1
            if result == False:
                sys.stderr.write("Error. Running the time course simulation failed.\n")
                if CCopasiMessage.size() > 0:
                    sys.stderr.write(CCopasiMessage.getAllMessageText(True))
                return 1
            timeSeries = trajectoryTask.getTimeSeries()
            # RecordedSteps are 1 + duration to account for initial state.
            assert timeSeries.getRecordedSteps() == (duration+1)

            # Parser implementation. Inserts two new strings at position 0 for iteration and logical inputs.
            if n == 0 and j == 0:
                with open(outputfilename, "r+") as ofn:
                    with open(parsedfilename, "w+") as pfn:
                        pfn.write(ofn.readline())
            lineparsed = TextParser(outputfilename, (duration+1))
            lineparsed.insert(0, outputnamevar)
            lineparsed.insert(0, str(n+1))
            parsedlines.append(lineparsed)

            with open(dumpfilename, "a+") as dfn:
                with open(outputfilename, "r+") as ofn:
                    dfn.writelines(ofn.readlines())

    LineCompiler(parsedlines, parsedfilename)

if (__name__ == '__main__'):
    main(sys.argv[1:])