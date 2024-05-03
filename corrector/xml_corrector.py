from lxml import etree
import re

class XMLCorrector:
    @staticmethod
    def modificar_xml(xml_string):
        try:
            root = etree.fromstring(xml_string)
            for element in root.iter():
                if element.text:
                    XMLCorrector._corrigir_numeros_4_casas(element)
            return etree.tostring(root, encoding='utf-8', method='xml').decode("utf-8")
        except etree.XMLSyntaxError:
            return "Erro XML: XML inválido."
    
    @staticmethod
    def _corrigir_numeros_4_casas(element):
        if re.match(r'^\d+(\.\d+)?$', element.text):
            # Verifica se o texto contém apenas números
            if element.tag.endswith('valorUnitario') or element.tag.endswith('valorTotal') or element.tag.endswith('valorProcedimentos') or element.tag.endswith('valorTotalGeral') or element.tag.endswith('reducaoAcrescimo'):
                # Arredonda para duas casas decimais se estiver nas tags mencionadas
                element.text = "{:.2f}".format(float(element.text))