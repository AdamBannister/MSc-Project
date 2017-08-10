from COPASI import *
from types import *
import sys

def main():
  assert CCopasiRootContainer.getRoot() != None
  # create a new datamodel
  dataModel = CCopasiRootContainer.addDatamodel()
  assert CCopasiRootContainer.getDatamodelList().size() == 1
  # get the model from the datamodel
  model = dataModel.getModel()
  assert model != None
  # set the units for the model
  # we want seconds as the time unit
  # microliter as the volume units
  # and nanomole as the substance units
  model.setTimeUnit(CUnit.s)
  model.setVolumeUnit(CUnit.microl)
  model.setQuantityUnit(CUnit.nMol)

  # we have to keep a set of all the initial values that are changed during
  # the model building process
  # They are needed after the model has been built to make sure all initial
  # values are set to the correct initial value
  changedObjects=ObjectStdVector()

  # create a compartment with the name cell and an initial volume of 5.0
  # microliter
  compartment = model.createCompartment("cell", 5.0)
  object = compartment.getInitialValueReference()
  assert object != None
  changedObjects.push_back(object)
  assert compartment != None
  assert model.getCompartments().size() == 1
  # create a new metabolite with the name glucose and an inital
  # concentration of 10 nanomol
  # the metabolite belongs to the compartment we created and is is to be
  # fixed
  glucose = model.createMetabolite("glucose", compartment.getObjectName(), 10.0, CMetab.FIXED)
  assert glucose != None
  object = glucose.getInitialConcentrationReference()
  assert object != None
  changedObjects.push_back(object)
  assert model.getMetabolites().size() == 1
  # create a second metabolite called glucose-6-phosphate with an initial
  # concentration of 0. This metabolite is to be changed by reactions
  g6p = model.createMetabolite("glucose-6-phosphate", compartment.getObjectName(), 0.0, CMetab.REACTIONS)
  assert g6p != None
  object = g6p.getInitialConcentrationReference()
  assert object != None
  changedObjects.push_back(object)
  assert model.getMetabolites().size() == 2
  # another metabolite for ATP, also fixed
  atp = model.createMetabolite("ATP", compartment.getObjectName(), 10.0, CMetab.FIXED)
  assert atp != None
  object = atp.getInitialConcentrationReference()
  assert object != None
  changedObjects.push_back(object)
  assert model.getMetabolites().size() == 3
  # and one for ADP
  adp = model.createMetabolite("ADP", compartment.getObjectName(), 0.0, CMetab.REACTIONS)
  assert adp != None
  object = adp.getInitialConcentrationReference()
  assert object != None
  changedObjects.push_back(object)
  assert model.getMetabolites().size() == 4
  # now we create a reaction
  reaction = model.createReaction("hexokinase")
  assert reaction != None
  assert model.getReactions().size() == 1
  # hexokinase converts glucose and ATP to glucose-6-phosphate and ADP
  # we can set these on the chemical equation of the reaction
  chemEq = reaction.getChemEq()
  # glucose is a substrate with stoichiometry 1
  chemEq.addMetabolite(glucose.getKey(), 1.0, CChemEq.SUBSTRATE)
  # ATP is a substrate with stoichiometry 1
  chemEq.addMetabolite(atp.getKey(), 1.0, CChemEq.SUBSTRATE)
  # glucose-6-phosphate is a product with stoichiometry 1
  chemEq.addMetabolite(g6p.getKey(), 1.0, CChemEq.PRODUCT)
  # ADP is a product with stoichiometry 1
  chemEq.addMetabolite(adp.getKey(), 1.0, CChemEq.PRODUCT)
  assert chemEq.getSubstrates().size() == 2
  assert chemEq.getProducts().size() == 2
  # this reaction is to be irreversible
  reaction.setReversible(False)
  assert reaction.isReversible() == False
  # now we ned to set a kinetic law on the reaction
  # maybe constant flux would be OK
  # we need to get the function from the function database
  funDB = CCopasiRootContainer.getFunctionList()
  assert funDB != None
  # it should be in the list of suitable functions
  # lets get all suitable functions for an irreversible reaction with  2 substrates
  # and 2 products
  suitableFunctions = funDB.suitableFunctions(2, 2, TriFalse)
  assert len(suitableFunctions) > 0
  function=None
  for f in suitableFunctions:
      # we just assume that the only suitable function with Constant in
      # it's name is the one we want
      if f.getObjectName().find("Constant") != -1:
          function=f
          break
  if function:
      # we set the function
      # the method should be smart enough to associate the reaction entities
      # with the correct function parameters
      reaction.setFunction(function)
      assert reaction.getFunction() != None
      # constant flux has only one function parameter
      assert reaction.getFunctionParameters().size() == 1
      # so there should be only one entry in the parameter mapping as well
      assert len(reaction.getParameterMappings()) == 1
      parameterGroup = reaction.getParameters()
      assert parameterGroup.size() == 1
      parameter = parameterGroup.getParameter(0)
      # make sure the parameter is a local parameter
      assert reaction.isLocalParameter(parameter.getObjectName())
      # now we set the value of the parameter to 0.5
      parameter.setValue(0.5)
      object = parameter.getValueReference()
      assert object != None
      changedObjects.push_back(object)
  else:
      sys.stderr.write("Error. Could not find a kinetic law that contains the term \"Constant\".\n" )
      return 1
  model.compileIfNecessary()

  # now that we are done building the model, we have to make sure all
  # initial values are updated according to their dependencies
  model.updateInitialValues(changedObjects)

  # save the model to a COPASI file
  # we save to a file named example1.cps, we don't want a progress report
  # and we want to overwrite any existing file with the same name
  # Default tasks are automatically generated and will always appear in cps
  # file unless they are explicitley deleted before saving.
  dataModel.saveModel("example1.cps", True)

  # export the model to an SBML file
  # we save to a file named example1.xml, we want to overwrite any
  # existing file with the same name and we want SBML L2V3
  dataModel.exportSBML("example1.xml", True, 2, 3)


#if(__name__ == '__main__'):
   #main()