# Change target name from documentation to actual target name
# Actual target names are read from properties file
# target - Target Name from Documentation
# returns - Target Name for Domain
def fixTargetName(target) :
  if target == 'OSB_Cluster' :
    return osb_target_name
  elif target == 'SOA_Cluster' :
    return soa_target_name
  elif target == 'BAM_Cluster' :
    return bam_target_name
  elif target == 'WSM-PM_Cluster' :
    return wsm_target_name
  elif target == 'WLS_OSB1' :
    return osb1_server_name
  elif target == 'AdminServer' :
    return admin_server_name
  else:
    return target

# Load resource and target data from file created from documentation
# File format is a one line with resource name followed by
# one line with comma separated list of targets
# fileIn - Resource & Target File
# accum - Dictionary containing mappings of expected Resource to Target
# returns - Dictionary mapping expected Resource to expected Target
def parseFile(fileIn, accum) :
  # Load resource name
  line1 = fileIn.readline().strip('\n')
  if line1 == '':
    # Done if no more resources
    return accum
  else:
    # Load list of targets
    line2 = fileIn.readline().strip('\n')
    # Convert string to list of targets
    targetList = map(fixTargetName, line2.split(','))
    # Associate resource with list of targets in dictionary
    accum[line1] = targetList
    # Parse remainder of file
    return parseFile(fileIn, accum)

# Load resources and targets from file
# filename - Filename to load
# returns - Dictionary mapping expected Resource to expected Target
def loadFile(filename) :
  tfile = open(filename)
  fList = parseFile(tfile, {})
  tfile.close()
  return fList

# Validate that resources are correctly targeted
# name - Name of Resource Type
# filename - Filename to validate against
# items - List of Resources to be validated
def validateDeployments(name, filename, items) :
  print name+' Check'
  print "====================================================="
  fList = loadFile(filename)
  # Iterate over resources
  for item in items:
    try:
      # Get expected targets for resource
      itemCheckList = fList[item.getName()]
      # Iterate over actual targets
      for target in item.getTargets() :
        try:
          # Remove actual target from expected targets
          itemCheckList.remove(target.getName())
        except ValueError:
          # Target not found in expected targets
          print 'Extra target: '+item.getName()+': '+target.getName()
      # Iterate over remaining expected targets, if any
      for refTarget in itemCheckList:
        print 'Missing target: '+item.getName()+': '+refTarget
    except KeyError:
      # Resource not found in expected resource dictionary
      print 'Extra '+name+' Deployed: '+item.getName()
  print

connect(admin_username,admin_password,admin_url)

domainConfig()

validateDeployments('Application',
                    verification_file_dir+'/verifyApps.txt',
                    cmo.getAppDeployments())
validateDeployments('Library',
                    verification_file_dir+'/verifyLibs.txt',
                    cmo.getLibraries())
validateDeployments('StartupClass',
                    verification_file_dir+'/verifyStartup.txt',
                    cmo.getStartupClasses())
validateDeployments('ShutdownClass',
                    verification_file_dir+'/verifyShutdown.txt',
                    cmo.getShutdownClasses())
validateDeployments('JMS Resource',
                    verification_file_dir+'/verifyJMS.txt',
                    cmo.getJMSSystemResources())
validateDeployments('WLDF Resource',
                    verification_file_dir+'/verifyWLDF.txt',
                    cmo.getWLDFSystemResources())
