#!/usr/bin/python

# Author: Adam Bannister, Newcastle University.

from COPASI import *
import sys
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
        x = re.sub('[^0123456789.e-]+', '', x)
        #print x
        lst.append(float(x))
    return(lst)

def LineCompiler(linelist, output_filename):
    "Sub-function to compile a list into a string and write it to a file."
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
    """Function to generate & simulate a range of COPASI models with changes in input concentration.
    Arguments: 'filename' is a string pointing to the model file in XML (SBML) format in the local directory.
    'minimum_concentration' is the minimum concentration of input in mmol/ml.
    'max_concentration' is the maximum concentration of input in mmol/ml.
    'iterations' is the number of models generated between the minimum and the maximum concentrations specified.
    'duration' is the time course duration in seconds. Step count = duration in seconds. Default = 5000.
    'speciesname' is name of species in XML file to change.
    """

    # 'args' is fed to the main function as a tuple. Defining variables & ensuring type is correct.
    filename = str(args[0])
    min_param = float(args[1])
    max_param = float(args[2])

    try:
        iterations = int(args[3])
    except IndexError:
        iterations = 10

    try:
        duration = int(args[4])
    except IndexError:
        duration = 50000

    reactionname = str(args[5])

    try:
        parametername = str(args[6])
    except IndexError:
        parametername = "k1"

    try:
        inputname = str(args[7])
    except IndexError:
        inputname = "inducer_1"

    try:
        inputconc = float(args[8])
    except IndexError:
        inputconc = 0.005

    assert isinstance(filename, str)
    assert isinstance(min_param, float)
    assert isinstance(max_param, float)
    assert isinstance(reactionname, str)
    assert isinstance(parametername, str)
    assert isinstance(iterations, int)

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
    outputfilename = filename[:-4] + "_p_output.txt"
    dumpfilename = "Dump_" + outputfilename
    with open(dumpfilename, "w+") as dfn:
        dfn.truncate(0)

    parsedfilename = "Parsed_" + outputfilename
    with open(parsedfilename, "w+") as pfn:
        pfn.truncate(0)

    # Setting input species to specific level from script.
    inputspecies = model.getMetabolite(inputname)
    inputspecies.setInitialConcentration(inputconc)
    object = inputspecies.getInitialConcentrationReference()
    changedObjects.push_back(object)
    model.updateInitialValues(changedObjects)
    model.compileIfNecessary()
    changedObjects = ObjectStdVector()

    # Defining the variable for model reaction to alter.
    reaction = model.getReaction(str(reactionname))
    assert reaction is not None

    # Generating models in a loop, per iteration.
    for n in range(iterations):
        iteration_increment = (float(n)/float(iterations-1)) * (float(max_param) - float(min_param))
        inputparam = min_param + iteration_increment
        # print "Input parameter as a variable is " + str(inputparam)
        reaction.setParameterValue(parametername, inputparam)
        # print "Parameter in the reaction is " + str(reaction.getParameterValue("k1"))
        object = reaction.getDataObject()
        changedObjects.push_back(object)
        model.updateInitialValues(changedObjects)
        model.compileIfNecessary()

        # Running a time course. Code adapted from Python-COPASI package - COPASI v4.19 - example scripts.
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
        if n == 0:
            with open(outputfilename, "r+") as ofn:
                with open(parsedfilename, "w+") as pfn:
                    pfn.write(ofn.readline())
        lineparsed = TextParser(outputfilename, (duration+1))
        lineparsed.insert(0, str(inputparam))
        parsedlines.append(lineparsed)

        with open(dumpfilename, "a+") as dfn:
            with open(outputfilename, "r+") as ofn:
                dfn.writelines(ofn.readlines())

    LineCompiler(parsedlines, parsedfilename)

if (__name__ == '__main__'):
    main(sys.argv[1:])
