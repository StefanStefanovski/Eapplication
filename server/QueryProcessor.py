from JDMResponse import *

from CSVModel import *

from selectolax.parser import HTMLParser
import urllib.parse
import requests as r
import re

class QueryProcessor:
    def __init__(self, url_prefix, url_postfix):
        self.url_prefix = url_prefix
        self.url_postfix = url_postfix
    
    def process(self, query):
        html = r.get(self.buildUrl(query.term))
        tree = HTMLParser(html.text)
        code_tag = tree.css_first('CODE')

        if not code_tag:
            return None
        
        code_text = code_tag.text()
        definition_tag = tree.css_first('def')
        definition = ''
        if definition_tag:
            definition = definition_tag.text()

        return self.processGet(query.term, query.properties, code_text, definition, query)
            
    def buildUrl(self, term):
        return self.url_prefix + term + self.url_postfix

    def processGet(self, term, properties, code, definition, query):
        response = JDMResponse()
        response.query_str = query.content
        response.definition = definition

        csv_lines = code.split('\n')
        csv_lines = [ line for line in csv_lines if (not line.startswith('//') and len(line) > 0)]
        csv_ds = csv.reader(csv_lines, delimiter=';')

        for entry in csv_ds:
            key = entry[0]
            if (key == CSVModel.KEY_NODE):
                    node = self.handleNode(entry, term)

                    if node is not None:
                        response.terms.append(node)

                        if node.isRefinement:
                            response.refinements.append(node)
            
            elif (key == CSVModel.KEY_RELATION):
                relation = self.handleRelation(entry)
                response.relations.append(relation)

        return response
                
    def handleNode(self, entry, term):
        depth = len(term.split('>'))

        try:
            nodeType = int(entry[CSVModel.INDEX_NODE_TYPE])
            nodeId = int(entry[CSVModel.INDEX_NODE_ID])
            nodeWeight = int(entry[CSVModel.INDEX_NODE_WEIGHT])
            formattedName = None
            isRefinement = False
            name = None

            if nodeType == CSVModel.NODE_TYPE_TERM:
                name = entry[CSVModel.INDEX_NODE_NAME].replace('\'', '')

                if len(entry) > 5:
                    formattedName = entry[CSVModel.INDEX_NODE_FORMATTED_NAME]
                    formattedName = formattedName.replace('\'', '')

                    if ">" in formattedName and (len(formattedName.split('>')) > depth) and formattedName.startswith(term + ">"):
                        isRefinement = True

            return Node(nodeId, name, nodeType, nodeWeight, formattedName, isRefinement)
        except ValueError:
            return None

    def handleRelation(self, entry):
        relation_id = int(entry[CSVModel.INDEX_RELATION_TYPE])
        node1 = int(entry[CSVModel.INDEX_RELATION_NODE1])
        node2 = int(entry[CSVModel.INDEX_RELATION_NODE2])
        relation_type = int(entry[CSVModel.INDEX_RELATION_TYPE])

        return Relation(relation_id, node1, node2, relation_type)
