# Função para corrigir o XML
from lxml import etree
import logging
from io import BytesIO

def corrigir_xml(arquivo):
    try:
        nome_arquivo = arquivo.filename
        xml_data = arquivo.read()
        parser = etree.XMLParser(recover=True)  # Permitir a recuperação de erros
        tree = etree.parse(BytesIO(xml_data), parser=parser)
        logging.info(f"XML corrigido com sucesso. Arquivo original: {nome_arquivo}")
        return etree.tostring(tree.getroot(), encoding='utf-8', method='xml').decode("utf-8")
    except etree.XMLSyntaxError:
        xml_data = arquivo.read()
        xml_data = xml_data.decode("utf-8")
        pos = xml_data.find('<')
        if pos > 0:
            xml_data = xml_data[pos:]
        xml_data = '<?xml version="1.0"?>' + xml_data
        return xml_data
    
def contar_guias(arquivo_xml):
    try:
        # Fazer o parsing do XML
        tree = etree.parse(arquivo_xml)
        
        tiss_version = find_padrao_tag(arquivo_xml)
        
        if tiss_version < '4.00.00':
            # Contar o número de elementos <ans:guiaSP-SADT>
            num_guias = len(tree.findall('.//ans:guiaSP-SADT', namespaces={'ans': 'http://www.ans.gov.br/padroes/tiss/schemas'}))
        else:
            num_guias = len(tree.findall('.//ans:cabecalhoGuia', namespaces={'ans': 'http://www.ans.gov.br/padroes/tiss/schemas'}))
        
        return num_guias
    
    except etree.XMLSyntaxError:
        print("Erro: O arquivo não é um XML válido.")
        return None
    
def extrair_numero_lote(arquivo_xml):
    try:
        # Fazer o parsing do XML
        tree = etree.parse(arquivo_xml)
        
        # Encontrar o elemento <ans:numeroLote>
        numero_lote_element = tree.find('.//ans:numeroLote', namespaces={'ans': 'http://www.ans.gov.br/padroes/tiss/schemas'})
        
        if numero_lote_element is not None:
            # Extrair o conteúdo da tag
            numero_lote = numero_lote_element.text
            return numero_lote
        else:
            return None
    
    except etree.XMLSyntaxError:
        return "Número da remessa não encontrado."
    
def extrair_valor_total(arquivo_xml):
    try:
        # Fazer o parsing do XML
        tree = etree.parse(arquivo_xml)
        
        tiss_version = find_padrao_tag(arquivo_xml)
        
        if tiss_version < '4.00.00':
            # Encontrar todos os elementos <ans:valorTotal>
            valor_total_elements = tree.findall('.//ans:valorTotalGeral', namespaces={'ans': 'http://www.ans.gov.br/padroes/tiss/schemas'})
        else:
            valor_total_elements = tree.findall('.//ans:valorTotal', namespaces={'ans': 'http://www.ans.gov.br/padroes/tiss/schemas'})
        
        valor_total_total = 0.0
        for valor_total_element in valor_total_elements:
            # Extrair o conteúdo da tag, remover espaços e quebras de linha, e converter para float
            valor_total_str = valor_total_element.text
            if valor_total_str is not None:
                valor_total_str = valor_total_str.strip()
                if valor_total_str:
                    valor_total = float(valor_total_str)
                    valor_total_total += valor_total
        
        return valor_total_total
    
    except etree.XMLSyntaxError:
        print("Erro: O arquivo não é um XML válido.")
        return None
    except ValueError:
        print("Erro: Não foi possível converter o valor total para um número válido.")
        return None
    
# Função para gravar o arquivo modificado
def gravar_arquivo(xml_string, nome_arquivo):
    try:
        with open(nome_arquivo, 'w') as f:
            f.write(xml_string)
    except Exception as e:
        return str(e)
    
from lxml import etree

# Função para encontrar a tag <ans:Padrao> e retornar a versão do TISS
def find_padrao_tag(xml_file):
    try:
        tree = etree.parse(xml_file)
        root = tree.getroot()
        namespace = {'ans': root.tag.split('}')[0][1:]}
        padrao_tag = root.find('.//ans:Padrao', namespace)
        return padrao_tag.text if padrao_tag is not None else None
    except etree.XMLSyntaxError:
        return None
