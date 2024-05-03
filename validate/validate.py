from lxml import etree
import os
from urllib.parse import unquote
import re

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
    
def validar_xml_contra_xsd(xml_path, xsd_path):
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
                return f"O XML é válido de acordo com o schema XSD fornecido. TISS {xsd_path} "
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
        return f"Erro desconhecido ao validar o XML: {e}. TISS {xsd_path}"