from COPASI import *
from types import *
import sys

# This is a sample script to show how to reassign model values.

# Make sure the root integrity is intact.
assert CCopasiRootContainer.getRoot() != None
# Adding a datamodel to the root container.
dataModel = CCopasiRootContainer.addDatamodel()
# Ensuring only one data model is present.
assert CCopasiRootContainer.getDatamodelList().size() == 1
# Importing from file. SBML version.
dataModel.importSBML("model1.xml")
# Defining the model as the next level down in the COPASI module hierarchy.
model = dataModel.getModel()
# Defining a vector of changed objects, which can then be pushed back onto the higher-level classes.
changedObjects = ObjectStdVector()
# Defining a metabolite as a variable. Can do this in a loop for multiple metabolites.
metabolite_A = model.getMetabolite("A")
assert metabolite_A != None
print type(metabolite_A)
# Print original value.
print("Initial concentration of A before changes is: {}").format(metabolite_A.getInitialConcentration())
# Setting the initial concentration to 1.0.
metabolite_A.setInitialConcentration(1.0)
# Print updated value.
print("Initial concentration of A after changes is: {}").format(metabolite_A.getInitialConcentration())
# Push back the changes to higher-level classes.
object = metabolite_A.getInitialConcentrationReference()
changedObjects.push_back(object)
#model.compileIfNecessary()
#model.updateInitialValues(changedObjects)
# Now checking to ensure this has been updated at 2 class variable levels. Testing 'model' variable
metabolite_A_test1 = model.getMetabolite("A")
print("Initial concentration of A in 'model'  is now: {}").format(metabolite_A_test1.getInitialConcentration())
# Testing 'datamodel' variable. Output should show the push_back method updates both higher-level classes.
modeltest = dataModel.getModel()
metabolite_A_test2 = modeltest.getMetabolite("A")
print("Initial concentration of A in 'dataModel' is now: {}").format(metabolite_A_test2.getInitialConcentration())