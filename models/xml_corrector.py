from lxml import etree
import re

class XMLCorrector:
    @staticmethod
    def modificar_xml(xml_string):
        try:
            root = etree.fromstring(xml_string)
            
            # Procura pelas tags 'ans:guiaSP-SADT' e, caso não encontre, procura por 'ans:guiasTISS'
            guias = [elem for elem in root.iter() if elem.tag.endswith('guiaSP-SADT') or elem.tag.endswith('guiasTISS')]
            
            for guia in guias:
                # Soma todos os valores nas tags 'valorTotal' dentro da mesma 'ans:guia'
                valor_total = sum(float(elem.text) for elem in guia.iter() if elem.tag.endswith('valorTotal') and elem.text.strip())
                
                # Verifica se a tag 'valorTotalGeral' existe
                valor_total_geral = next((elem for elem in guia.iter() if elem.tag.endswith('valorTotalGeral')), None)
                if valor_total_geral is not None:
                    valor_total_geral.text = "{:.2f}".format(valor_total)
                
            # Corrige os números de 4 casas decimais
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
            if element.tag.endswith('valorUnitario') or element.tag.endswith('valorTotal') or element.tag.endswith('valorProcedimentos') or element.tag.endswith('reducaoAcrescimo'):
                # Arredonda para duas casas decimais se estiver nas tags mencionadas
                element.text = "{:.2f}".format(float(element.text))