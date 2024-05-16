import re
from decimal import Decimal, ROUND_HALF_UP
from lxml import etree
from controllers.tiss_controller import tiss_inferior_a_4, tiss_superior_a_4

class XMLParameters:
    @staticmethod
    def modificar_xml(xml_string):
        try:
            root = etree.fromstring(xml_string)
            namespace = {'ans': root.tag.split('}')[0][1:]}

            # Procurar pela tag <ans:Padrao>
            tiss_version = root.find('.//ans:Padrao', namespace)

            if tiss_inferior_a_4(tiss_version.text):
                # Corrige os números de 4 casas decimais
                for element in root.iter():
                    if element.text and re.match(r'^\d+(\.\d{4,})$', element.text):
                        XMLParameters._corrigir_numeros_4_casas(element)

                guias_sadt = [elem for elem in root.iter() if elem.tag.endswith('guiaSP-SADT')]
                guias_resumo = [elem for elem in root.iter() if elem.tag.endswith('guiaResumoInternacao')]

                if guias_sadt:
                    for guia_sadt in guias_sadt:
                        valor_total_geral = guia_sadt.find('.//ans:valorTotalGeral', namespace)
                        if valor_total_geral is not None:
                            # Soma todos os valores nas tags 'valorTotal' dentro da mesma 'ans:guiaSP-SADT'
                            valor_total = sum(Decimal(elem.text) for elem in guia_sadt.iter() if elem.tag.endswith('valorTotal') and elem.text.strip())
                            # Atualiza com o valor total antes do arredondamento
                            valor_total_geral.text = XMLParameters._format_decimal(valor_total)

                elif guias_resumo:
                    for guia_resumo in guias_resumo:
                        valor_total_geral = guia_resumo.find('.//ans:valorTotalGeral', namespace)

            elif tiss_superior_a_4(tiss_version.text):
                # Apenas arredonda os números de 4 casas decimais para 2 casas decimais
                for element in root.iter():
                    if element.text and re.match(r'^\d+(\.\d{4,})$', element.text):
                        element.text = XMLParameters._format_decimal(Decimal(element.text))

            return etree.tostring(root, encoding='utf-8', method='xml').decode("utf-8")
        except etree.XMLSyntaxError:
            return "Erro XML: XML inválido."

    @staticmethod
    def _corrigir_numeros_4_casas(element):
        # Verifica se o texto contém apenas números
        if re.match(r'^\d+(\.\d+)?$', element.text):
            # Arredonda para duas casas decimais se estiver nas tags mencionadas
            if element.tag.endswith('valorUnitario') or element.tag.endswith('valorTotal') or element.tag.endswith('valorProcedimentos') or element.tag.endswith('reducaoAcrescimo'):
                element.text = XMLParameters._format_decimal(Decimal(element.text))

    @staticmethod
    def _format_decimal(value):
        # Arredonda corretamente para duas casas decimais com ROUND_HALF_UP
        return str(value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))