# -*- coding: utf-8 -*-
import codecs, pickle
from xml.dom import minidom

from java.net import URL
from javax.xml.xpath import XPathFactory, XPath, XPathConstants
from oracle.xml.parser.v2 import DOMParser
from java.io import FileReader

from tvutils import XhtmlNamespaceResolver


class TargetValidator(object):
    """ Download requirement maps from Oracle documentation and then check they're correct in
    clustered SOA environments.
    """

    def _fixMappings(self):
        # unfortunately, the doc is wrong! ad-hoc fixes here

        # singletons
        for app in ['ALSB Cluster Singleton Marker Application',
                    'ALSB Domain Singleton Marker Application',
                    'Message Reporting Purger']:
            # remove target OSB_Cluster
            self.mappings['Application'][app] = [
                s for s in self.mappings['Application'][app] if s != self.LOCALSERVERS['OSB_Cluster']
            ]
            # add target WLS_OSB1
            self.mappings['Application'][app].append(self.LOCALSERVERS['WLS_OSB1'])

        # add frevvo app
        self.mappings['Application']['frevvo'] = [self.LOCALSERVERS['SOA_Cluster']]

        # add OWSM Policy Support
        self.mappings['Application']['OWSM Policy Support in OSB Initializer Application'] = [
            self.LOCALSERVERS['SOA_Cluster'],
            self.LOCALSERVERS['AdminServer']
        ]

        # add missing lib
        self.mappings['Library']['oracle.bi.adf.model.slib#1.0-AT-11.1.1.2-DOT-0'] = [
            self.LOCALSERVERS['SOA_Cluster'],
            self.LOCALSERVERS['OSB_Cluster'],
            self.LOCALSERVERS['BAM_Cluster'],
            self.LOCALSERVERS['AdminServer']
        ]

        #add missing lib target
        self.mappings['Library']['oracle.bi.adf.model.slib#1.0-AT-11.1.1.2-DOT-0'].append(
            self.LOCALSERVERS['BAM_Cluster'])

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
            'WLDF Resource':    ('WLDF System Resource Targets',                            cmo.getWLDFSystemResources),
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
       # cleanup required by doc errors
        self._fixMappings()

    def saveMapping(self, fileName):
        domImp = minidom.getDOMImplementation()
        dom = domImp.createDocument(None,"mappings",None)
        root = dom.documentElement
        for itemType in self.mappings:
            mapElement = dom.createElement('itemType')
            mapElement.setAttribute('name',itemType)
            root.appendChild(mapElement)
            for item in self.mappings[itemType]:
                mapItem = dom.createElement('item')
                mapItem.setAttribute('name',item)
                mapElement.appendChild(mapItem)
                for target in self.mappings[itemType][item]:
                    mapTarget = dom.createElement('target')
                    mapTarget.setAttribute('name',target)
                    mapItem.appendChild(mapTarget)

        fp = codecs.open(fileName, 'w', encoding='utf-8')
        dom.writexml(fp, '', ' ', "\n")
        fp.close()
        #cleanup to save memory
        dom.unlink()

    def loadMapping(self, fileName):
        # first, clean up everything
        self.mappings = {}

        fr = FileReader(fileName)
        parser = DOMParser()
        parser.parse(fr)
        doc = parser.getDocument()
        e = doc.documentElement
        itNodes = e.getChildrenByTagName('itemType')
        for i in xrange(0,itNodes.getLength()):
            iType = itNodes.item(i)
            typeName = iType.getAttribute('name')
            self.mappings[typeName] = {}
            iNodes = iType.getChildrenByTagName('item')
            for n in xrange(0, iNodes.getLength()):
                item = iNodes.item(n)
                itemName = item.getAttribute('name')
                self.mappings[typeName][itemName] = []
                tNodes = item.getChildrenByTagName('target')
                for t in xrange(0, tNodes.getLength()):
                    target = tNodes.item(t)
                    self.mappings[typeName][itemName].append(target.getAttribute('name'))




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