# -*- coding: utf-8 -*-
from javax.xml.namespace import NamespaceContext;
from javax.xml import XMLConstants


class XhtmlNamespaceResolver(NamespaceContext):
    def getNamespaceURI(self, prefix):
        if prefix == XMLConstants.DEFAULT_NS_PREFIX:
            return "http://www.w3.org/1999/xhtml"
        else:
            return XMLConstants.NULL_NS_URI

    def getPrefix(self, namespaceURI):
        return None

    def getPrefixes(self, namespaceURI):
        return None