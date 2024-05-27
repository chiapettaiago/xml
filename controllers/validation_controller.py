from lxml import etree
import os
from urllib.parse import unquote
import re
import logging
from io import BytesIO

class SchemaResolver(etree.Resolver):
    def __init__(self, schema_path):
        super().__init__()
        self.schema_path = schema_path

    def resolve(self, url, pubid, context):
        if url.startswith('file:/'):
            path = unquote(url.replace('file:/', ''))
        else:
            path = os.path.join(self.schema_path, url)

        if re.match(r'^/[a-zA-Z]:', path):
            path = path[1:]

        return self.resolve_filename(path, context)
    
def listar_versoes_tiss(diretorio_schema):
    versoes = set()
    regex = re.compile(r"tissV(\d+_\d+_\d+).xsd")
    for arquivo in os.listdir(diretorio_schema):
        match = regex.search(arquivo)
        if match:
            versoes.add(match.group(1).replace('_', '.'))
    return sorted(versoes)

def find_padrao_tag(xml_file):

    # Carregar o arquivo XML
    tree = etree.parse(xml_file)
    root = tree.getroot()
    
    # Obter o namespace a partir do elemento raiz
    namespace = {'ans': root.tag.split('}')[0][1:]}
    
    # Procurar pela tag <ans:Padrao>3.05.00</ans:Padrao>
    padrao_tag = root.find('.//ans:Padrao', namespace)
    
    return padrao_tag.text

def find_operadora(xml_file):
    # Carregar o arquivo XML
    tree = etree.parse(xml_file)
    root = tree.getroot()
    
    # Obter o namespace a partir do elemento raiz
    namespace = {'ans': root.tag.split('}')[0][1:]}
    
    # Procurar pela tag <ans:Padrao>3.05.00</ans:Padrao>
    operadora = root.find('.//ans:registroANS', namespace)
    
    return operadora.text

def find_transacao(xml_file):
    # Carregar o arquivo XML
    tree = etree.parse(xml_file)
    root = tree.getroot()
    
    # Obter o namespace a partir do elemento raiz
    namespace = {'ans': root.tag.split('}')[0][1:]}
    
    # Procurar pela tag <ans:Padrao>3.05.00</ans:Padrao>
    tipo = root.find('.//ans:tipoTransacao', namespace)
    
    return tipo.text

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
    
def validar_xml_contra_xsd(xml_path, xsd_path, tiss_version):
    try:
        with open(xsd_path, 'rb') as xsd_file:
            schema_doc = etree.parse(xsd_file)

        schema = etree.XMLSchema(schema_doc)
        
        codificacoes = ['utf-8', 'iso-8859-1', 'windows-1252']  # Adicione mais codificações se necessário
        for cod in codificacoes:
            try:
                with open(xml_path, 'rb') as xml_file:
                    xml_doc = etree.parse(xml_file)
                    for elem in xml_doc.iter():
                        if elem.text is None:
                            elem.text = ""
                schema.assertValid(xml_doc)
                return f"O XML é válido de acordo com o schema XSD fornecido. TISS {tiss_version} "
            except IOError as e:
                print(f"Falha ao abrir o arquivo {xml_path}: {e}")
                return f"Falha ao abrir o arquivo: {e}"
            except UnicodeDecodeError as e:
                print(f"Falha ao ler o arquivo XML {xml_path} com a codificação {cod}: {e}")
                return f"Falha ao ler o arquivo XML com a codificação {cod}: {e}"
            except etree.XMLSyntaxError as e:
                print(f"Erro de análise XML no arquivo {xml_path}: {e}")
                return f"Erro de análise XML: {e}"


    except IOError as e:
        return f"Erro ao carregar o schema XSD: {e}"
    except etree.XMLSchemaError as e:
        return f"Erro ao validar o XML: {e}"
    except Exception as e:
        return f"Erro desconhecido ao validar o XML: {e}. TISS {tiss_version}"