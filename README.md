VerifySOACluster
================

Scripts to validate SOA cluster configuration by using Oracle-documented lists of targets for all object types

Inspired by [Anthony Reynolds' blog post](https://blogs.oracle.com/reynolds/entry/target_verification).

Quick usage
-----------

Edit verifyTargets.properties to point to your own installation, 
make sure your Admin Console is running, then launch verifyTargets.cmd/.sh.

Advanced Usage
--------------

Launch vtWLST.cmd/.sh, then:

    >>> # define local server mapping
    >>> localServers = {
            'OSB_Cluster': 'your_OSB_cluster_name',
            'SOA_Cluster': 'your_SOA_cluster_name',
            'BAM_Cluster': 'your_BAM_cluster_name',
            'WSM-PM_Cluster': 'your_WSMPM_cluster_name',
            'WLS_OSB1': 'your_WLS_cluster_name',
            'AdminServer': 'your_AdminServer_name',
        }

    >>> # connect (MUST precede object creation)
    >>> connect(admin_username,admin_password,admin_url)
    >>> domainConfig()

    >>> from targetvalidator import TargetValidator
    >>> tv = TargetValidator(cmo,localServers)

    >>> # download mappings from the Oracle site
    >>> tv.downloadMapping()

    >>> # save mappings locally
    >>> tv.saveMapping('/path/to/mapfile')

    >>> # load previously-saved mappings
    >>> tv.loadMapping('/path/to/mapfile')

    >>> # validate specific deployment type. Use .prettyValidateDeployments() for printed output
    >>> tv.validateDeployments('Application')
    {'missing': {'Ftp Transport Provider': ['OSB_Cluster'] }, 'extra': {'OracleBPMWorkspace': ['AdminServer']}

    >>> # available types
    >>> tv.mappings.keys()
    ['JMS Resource', 'WLDF Resource', 'ShutdownClass', 'Application', 'StartupClass', 'Library']
  
Feedback
========

Feel free to post issues or ping me at g.lacava@gmail.com .
