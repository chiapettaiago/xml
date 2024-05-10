# Função para validar o XML contra o XSD correspondente ao TISS
import re
import platform
import os
from controllers.validation_controller import validar_xml_contra_xsd
from controllers.xml_controller import find_padrao_tag


if platform.system() == 'Windows':
    SCHEMA_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'schemas\\')
elif platform.system() == 'Linux':
    SCHEMA_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'schemas/')

def validar_tiss(xml_path):
    try:
        tiss_versions = listar_versoes_tiss(SCHEMA_FOLDER)  # Substitua pelo seu caminho
        tiss_version = find_padrao_tag(xml_path)
        if tiss_version is None:
            return "Não foi possível encontrar a versão do TISS no XML."
        if tiss_version not in tiss_versions:
            return f"Versão do TISS ({tiss_version}) não suportada."
        
        xsd_path = f"/caminho/para/schema/tiss/tissV{tiss_version.replace('.', '_')}.xsd"  # Substitua pelo seu caminho
        return validar_xml_contra_xsd(xml_path, xsd_path)
    except Exception as e:
        return f"Erro ao validar o XML contra o XSD: {e}"
    

# Função para listar as versões do TISS disponíveis
def listar_versoes_tiss(diretorio_schema):
    versoes = set()
    regex = re.compile(r"tissV(\d+_\d+_\d+).xsd")
    for arquivo in os.listdir(diretorio_schema):
        match = regex.search(arquivo)
        if match:
            versoes.add(match.group(1).replace('_', '.'))
    return sorted(versoes)