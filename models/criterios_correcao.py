import re
from decimal import Decimal, ROUND_HALF_UP
from lxml import etree
from controllers.schema_controller import tiss_inferior_a_4, tiss_superior_a_4

class XMLParameters:
    @staticmethod
    def modificar_xml(xml_string):
        try:
            root = etree.fromstring(xml_string)
            namespace = {'ans': root.tag.split('}')[0][1:]}

            # Procurar pela tag <ans:Padrao>
            tiss_version = root.find('.//ans:Padrao', namespace)
            if tiss_version is not None and tiss_version.text is not None:
                if tiss_inferior_a_4(tiss_version.text):
                    for element in root.iter():
                        if element.text and re.match(r'^\d+(\.\d{4,})$', element.text):
                            if re.match(r'^\d+(\.\d+)?$', element.text):
                                if element.tag.endswith('valorUnitario') or element.tag.endswith('valorTotal') or element.tag.endswith('valorProcedimentos') or element.tag.endswith('reducaoAcrescimo'):
                                    element.text = str(Decimal(element.text).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))

                    guias_sadt = [elem for elem in root.iter() if elem.tag.endswith('guiaSP-SADT')]
                    guias_resumo = [elem for elem in root.iter() if elem.tag.endswith('guiaResumoInternacao')]
                    
                    #Critérios para guias de sadt
                    if guias_sadt:
                        for guia_sadt in guias_sadt:
                            valor_total_geral = guia_sadt.find('.//ans:valorTotalGeral', namespace)
                            if valor_total_geral is not None:
                                valor_total = sum(Decimal(elem.text) for elem in guia_sadt.iter() if elem.tag.endswith('valorTotal') and elem.text.strip())
                                valor_total_geral.text = str(valor_total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))

                    #Critérios para guias de resumo
                    elif guias_resumo:
                        for guia in guias_resumo:
                            soma_valor_total = Decimal('0.00')
                            for procedimento in guia.findall('.//ans:procedimentosExecutados//ans:valorTotal', namespace):
                                if procedimento is not None and procedimento.text:
                                    soma_valor_total += Decimal(procedimento.text)
                            
                            valor_procedimentos = guia.find('.//ans:valorProcedimentos', namespace)
                            if valor_procedimentos is not None:
                                valor_procedimentos.text = str(soma_valor_total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))

                            for servico in guia.findall('.//ans:servicosExecutados', namespace):
                                valor_unitario = servico.find('.//ans:valorUnitario', namespace)
                                reducao_acrescimo = servico.find('.//ans:reducaoAcrescimo', namespace)
                                valor_total = servico.find('.//ans:valorTotal', namespace)
                                            
                                if (valor_unitario is not None and valor_unitario.text and
                                    reducao_acrescimo is not None and reducao_acrescimo.text and
                                    valor_total is not None):
                                    valor_calculado = Decimal(valor_unitario.text) * Decimal(reducao_acrescimo.text)
                                    valor_total.text = str(valor_calculado.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
                            
                            tags_para_somar = [
                                'valorProcedimentos', 'valorDiarias', 'valorTaxasAlugueis',
                                'valorMateriais', 'valorMedicamentos', 'valorOPME', 'valorGasesMedicinais'
                            ]
                            
                            total_geral = Decimal('0.00')
                            for tag in tags_para_somar:
                                elemento = guia.find(f'.//ans:{tag}', namespace)
                                if elemento is not None and elemento.text:
                                    total_geral += Decimal(elemento.text)
                            
                            valor_total_geral = guia.find('.//ans:valorTotalGeral', namespace)
                            if valor_total_geral is not None:
                                valor_total_geral.text = str(total_geral.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))

                elif tiss_superior_a_4(tiss_version.text):
                    for element in root.iter():
                        if element.text and re.match(r'^\d+(\.\d{4,})$', element.text):
                            element.text = str(Decimal(element.text).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))

                return etree.tostring(root, encoding='utf-8', method='xml').decode("utf-8")
        except etree.XMLSyntaxError:
            return "Erro XML: XML inválido."
