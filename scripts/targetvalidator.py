# -*- coding: utf-8 -*-
import codecs, pickle

from java.net import URL
from javax.xml.xpath import XPathFactory, XPath, XPathConstants
from oracle.xml.parser.v2 import DOMParser

from tvutils import XhtmlNamespaceResolver


class TargetValidator(object):
    """ Download requirement maps from Oracle documentation and then check they're correct in
    clustered SOA environments.
    """

    def __init__(self, cmo, localServers):

        # default page for 11.1.1.x
        self.url = 'http://docs.oracle.com/cd/E28280_01/core.1111/e12036/target_appendix_soa.htm'

        # retrieve values passed by properties file
        self.LOCALSERVERS = localServers

        # map item types to table in doc and actual retrieval method
        self.PARSEMAP = {
            # item type : ( table title, method to retrieve actual system items )
            'Application':      ('SOA Application Targets',                                 cmo.getAppDeployments),
            'Library':          ('Oracle SOA Enterprise Deployment Targeting Library',      cmo.getLibraries),
            'StartupClass':     ('Oracle SOA Enterprise Deployment Startup Class Targets',  cmo.getStartupClasses),
            'ShutdownClass':    ('SOA EDG targeting shutdown class',                        cmo.getShutdownClasses),
            'JMS Resource':     ('JMS System Resource Targets',                             cmo.getJMSSystemResources),
            'WLDF Resource':    ('WLDF System Resource Targets',                            cmo.getWLDFSystemResources)
        }

        # where we'll store the mappings
        self.mappings = {}

        # init utility XPath object
        xpFactory = XPathFactory.newInstance()
        self.xp = xpFactory.newXPath()
        # namespace resolution is compulsory!!
        self.xp.setNamespaceContext(XhtmlNamespaceResolver())

    def _parseMapping(self, domObject, tableTitle, mappingTarget):
        """Find the table for a given target type, parse it and save the mappings
        :param domObject: DOM object supporting XPath manipulation
        :param tableTitle: title of table to search for
        :param mappingTarget: item type to associate
        """

        # get all rows
        rowNodes = self.xp.evaluate(
            "//:table[@title='%s']/:tbody/:tr" % tableTitle,
            domObject,
            XPathConstants.NODESET
        )
        # create dict in global mappings store
        if mappingTarget not in self.mappings:
            self.mappings[mappingTarget] = {}

        # for each row...
        for i in xrange(0, rowNodes.getLength()):

            # ... get all tds ...
            tds = rowNodes.item(i).getChildrenByTagName('td')
            # ... textContent will have \n at both ends, strip it ...
            item = tds.item(0).textContent.strip()
            # ... replace example names with real ones, so that we get a list of targets ...
            targets = [self.LOCALSERVERS[tName] for tName in tds.item(1).textContent.strip().split(',') if tName in self.LOCALSERVERS]
            # ... all done, save it!
            self.mappings[mappingTarget][item] = targets

    def downloadMapping(self):
        # download and parse the page
        urlObj = URL(self.url)
        parser = DOMParser()
        parser.parse(urlObj)
        doc = parser.getDocument()
        # for each type we know of, find table and method from our dict and build the actual mapping
        for itemType in self.PARSEMAP.keys():
            tableName, sysMethod = self.PARSEMAP[itemType]
            self._parseMapping(doc, tableName, itemType)

    # TODO: save/load is currently quite crude, would be better to generate human-readable files
    def saveMapping(self, fileName):
        fp = codecs.open(fileName, 'w', encoding='utf-8')
        pickle.dump(self.mappings, fp, 0)
        fp.close()

    def loadMapping(self, fileName):
        fp = codecs.open(fileName, 'r', encoding='utf-8')
        self.mappings = pickle.load(fp)
        fp.close()

    def validateDeployments(self, itemType):
        """ take a type of items to check, and return a dictionary with 'missing' and 'extra' targets
        :param itemType: string indicating the type of object to test
        :rtype result: dict {'missing': {'item name': 'missing targets'}, 'extra': {'item name': 'extra targets'} }
        """
        tableName, getItems = self.PARSEMAP[itemType]
        result = {'missing': {}, 'extra': {}}
        for item in getItems():
            itemName = item.getName()
            expectedTargets = self.mappings[itemType][itemName]
            realTargets = item.getTargets()
            missingTargets = [x for x in expectedTargets if x not in realTargets]
            extraTargets = [x for x in realTargets if x not in expectedTargets]
            if len(missingTargets) > 0:
                result['missing'][itemName] = missingTargets
            if len(extraTargets) > 0:
                result['extra'][itemName] = extraTargets
        return result

    def prettyValidateDeployments(self,itemType):
        """ same as validateDeployments, but prints results to terminal
        :param itemType: string indicating the type of object to test
        """
        result = self.validateDeployments(itemType)
        if len(result['missing'].keys()) > 0:
            for item in result['missing']:
                print "========"
                print "%(itemType)s : %(itemName)s is missing on %(missing)s" % {
                    'itemType': itemType,
                    'itemName': item,
                    'missing': ', '.join(result['missing'][item])
                }
        if len(result['extra'].keys() > 0):
            for item in result['extra']:
                print "========"
                print "%(itemType)s : %(itemName)s is present on %(extra)s but is unnecessary" % {
                    'itemType': itemType,
                    'itemName': item,
                    'extra': ', '.join(result['extra'][item])
                }