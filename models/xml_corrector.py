import re
from lxml import etree
from controllers.tiss_controller import tiss_inferior_a_4, tiss_superior_a_4

class XMLParameters:
    @staticmethod
    def modificar_xml(xml_string):
        try:
            root = etree.fromstring(xml_string)
            namespace = {'ans': root.tag.split('}')[0][1:]}
            
            # Procurar pela tag <ans:Padrao>3.05.00</ans:Padrao>
            tiss_version = root.find('.//ans:Padrao', namespace)
            
            
            if tiss_inferior_a_4(tiss_version.text):
                # Corrige os números de 4 casas decimais
                for element in root.iter():
                    if element.text and re.match(r'^\d+(\.\d+)?$', element.text):
                        XMLParameters._corrigir_numeros_4_casas(element)
                
                guias_sadt = [elem for elem in root.iter() if elem.tag.endswith('guiaSP-SADT')]
                guias_tiss = [elem for elem in root.iter() if elem.tag.endswith('guiasTISS')]
                
                
                if guias_tiss:
                    for guia_tiss in guias_tiss:
                        valor_total_geral = guia_tiss.find('.//ans:valorTotalGeral', namespace)
                        
                        # Soma todos os valores nas tags 'valorTotal' dentro da mesma 'ans:guiaSP-SADT'
                        valor_total = sum(float(elem.text) for elem in guia_tiss.iter() if elem.tag.endswith('valorTotal') and elem.text.strip())
                        valor_total_geral.text = "{:.2f}".format(valor_total)

                else:
                    for guia_sadt in guias_sadt:
                        valor_total_geral = guia_sadt.find('.//ans:valorTotalGeral', namespace)
                        
                        # Soma todos os valores nas tags 'valorTotal' dentro da mesma 'ans:guiaSP-SADT'
                        valor_total = sum(float(elem.text) for elem in guia_sadt.iter() if elem.tag.endswith('valorTotal') and elem.text.strip())
                        valor_total_geral.text = "{:.2f}".format(valor_total)
                    
                    
            elif tiss_superior_a_4(tiss_version.text):
               # Apenas arredonda os números de 4 casas decimais para 2 casas decimais
                for element in root.iter():
                    if element.text and re.match(r'^\d+(\.\d{4,})$', element.text):
                        element.text = "{:.2f}".format(float(element.text))

            return etree.tostring(root, encoding='utf-8', method='xml').decode("utf-8")
        except etree.XMLSyntaxError:
            return "Erro XML: XML inválido."

    @staticmethod
    def _corrigir_numeros_4_casas(element):
        # Verifica se o texto contém apenas números
        if re.match(r'^\d+(\.\d+)?$', element.text):
            # Arredonda para duas casas decimais se estiver nas tags mencionadas
            if element.tag.endswith('valorUnitario') or element.tag.endswith('valorTotal') or element.tag.endswith('valorProcedimentos') or element.tag.endswith('reducaoAcrescimo'):
                element.text = "{:.2f}".format(float(element.text))