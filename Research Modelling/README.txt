=== MSc Project Source Code - Adam Bannister - Newcastle University 2016/17 ===

Scripts contained:
ConcentrationRun.py
ConcentrationPlot.py
ParameterRun.py
Parameterplot.py

All scripts designed for Python 2.7.13, for COPASI and its Python bindings version 4.19.

Specification for XML input files: SBML 2 standard with following units: volume in ml, concentrations in mmol/ml, time in seconds. Scripts untested with other units.

=== ConcentrationRun.py ===

Function: runs COPASI time-course simulations while modifying the initial concentration value for a designated chemical species.

Usage: windows command line. Arguments, in order, are:
filename 		:: Name of an XML model conforming to SBML 2 standard in the local directory
min_concentration 	:: Minimum concentration for the species in mmol/ml.
max_concentration	:: Maximum concentration for the species in mmol/ml.
iterations		:: Number of models to generate & run between the min and max concentrations, default 10.
duration		:: Duration for COPASI time course. Default: 50000s.
speciesname		:: Name of the species to change as it is written in the XML file. Default: "inducer_1"

Example usage, to use a model named Model1.xml and generate 6 models between 0 and 1.0 mmol/ml concentration of the species inducer_A and run these for 40,000 seconds:

python ConcentrationRun.py Model1.xml 0 1 6 40000 inducer_A

Output format: 3 text files. 
1 paging file: 	(filename)_output.txt
1 dump file:	Dump_(filename)_output.txt
1 parsed file:	Parsed_(filename)_output.txt

Output files have bespoke implied structure.

Python dependencies: Python-COPASI bindings, sys, re

=== ConcentrationPlot.py ===

Function: uses bespoke layout txt file from ConcentrationRun.py to plot results

Usage: windows command line. Arguments, in order, are:
filename		:: Name of .txt file in local directory: Parsed file from ConcentrationRun.py.
inputname		:: Name of the input species to be plot on the x-axis.
outputname		:: Name of the output species to be plot on the y-axis.
logxYN			:: Optional argument for whether to log x-axis; set to Y for yes or N for no. Default: N

Example usage, to plot parsed Model1.xml's output from the ConcentrationRun script, with input named inducer_A and output named GFP and to log the x-axis:

python ConcentrationPlot.py Parsed_Model1_output.txt inducer_A GFP N

Output style: opens MatPlotLib plot for saving/examination.

Python dependencies: matplotlib.pyplot, sys

=== ParameterRun.py ===

Function: runs COPASI time-course simulations while modifying the value for a parameter of a specific reaction in the model.

Usage: windows command line. Arguments, in order, are:
filename 		:: Name of an XML model conforming to SBML 2 standard in the local directory
min_param		:: Minimum parameter value. Units assigned by COPASI.
max_param		:: Maximum parameter value. Units assigned by COPASI.
iterations		:: Number of models to generate & run between the min and max for parameter, default 10.
duration		:: Duration for COPASI time course. Default: 50000s.
reactionname		:: Name of the reaction containing specific parameter, as it is written in the XML file.
parametername		:: Name of the parameter in the designated reaction. Default: "k1"
inputname		:: Name of the input species in the XML file.
inputconc		:: Concentration of input species to set when running the model in mmol/ml. Default: 0.005

Example usage, to use a model named Model1.xml and simulate 6 models with a range of parameter "k2" values from reaction "GFP_transcription" that are between 0 and 10000. Simulations run for 40,000 seconds, input "inducer_A" is set to a concentration of 0.01 mmol/ml.

python ParameterRun.py Model1.xml 0 10000 6 40000 GFP_transcription k2 inducer_A 0.01

Output format: 3 text files. 
1 paging file: 	(filename)_p_output.txt
1 dump file:	Dump_(filename)_p_output.txt
1 parsed file:	Parsed_(filename)_p_output.txt

Output files have bespoke implied structure.

Python dependencies: Python-COPASI bindings, sys, re

=== ParameterPlot.py ===

Function: uses bespoke layout txt file from ParameterRun.py to plot results. Plots parameter on x-axis using the parameter value written in the parsed file.

Usage: windows command line. Arguments, in order, are:
filename		:: Name of .txt file in local directory: Parsed file from ParameterRun.py.
outputname		:: Name of the output species to be plot on the y-axis.
logxYN			:: Optional argument for whether to log x-axis; set to Y for yes or N for no. Default: N

Example usage, to plot parsed Model1.xml's output from the ConcentrationRun script, with input named inducer_A and output named GFP and to log the x-axis:

python ConcentrationPlot.py Parsed_Model1_output.txt inducer_A GFP N

Output style: opens MatPlotLib plot for saving/examination.

Python dependencies: matplotlib.pyplot, sys