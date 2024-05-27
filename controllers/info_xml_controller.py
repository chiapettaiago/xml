# Função para corrigir o XML
from lxml import etree

    
def nome_xml(arquivo):
    nome_arquivo = arquivo.filename
    return nome_arquivo
    
def contar_guias(arquivo_xml):
    try:
        # Fazer o parsing do XML
        tree = etree.parse(arquivo_xml)
        
        tiss_version = find_padrao_tag(arquivo_xml)
        
        if tiss_version < '4.00.00':
            # Contar o número de elementos <ans:guiaSP-SADT>
            num_guias = len(tree.findall('.//ans:guiaSP-SADT', namespaces={'ans': 'http://www.ans.gov.br/padroes/tiss/schemas'}))
            if num_guias == 0:
                num_guias = len(tree.findall('.//ans:guiaResumoInternacao', namespaces={'ans': 'http://www.ans.gov.br/padroes/tiss/schemas'}))
        else:
            num_guias = len(tree.findall('.//ans:cabecalhoGuia', namespaces={'ans': 'http://www.ans.gov.br/padroes/tiss/schemas'}))
        
        return num_guias
    
    except etree.XMLSyntaxError:
        print("Erro: O arquivo não é um XML válido.")
        return None
    

def tipo_guia(arquivo_xml):
    try:
        # Fazer o parsing do XML
        tree = etree.parse(arquivo_xml)
        
        guia = len(tree.findall('.//ans:guiaSP-SADT', namespaces={'ans': 'http://www.ans.gov.br/padroes/tiss/schemas'}))
        guia_tipo = "Guia de SP-SADT"
        if guia == 0:
            guia = len(tree.findall('.//ans:guiaResumoInternacao', namespaces={'ans': 'http://www.ans.gov.br/padroes/tiss/schemas'}))
            guia_tipo = "Guia de Resumo de Internação"
            
        return guia_tipo
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
