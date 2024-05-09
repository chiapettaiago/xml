from flask import Flask, render_template, request, redirect, url_for, send_file
from validate.validate import listar_versoes_tiss, validar_xml_contra_xsd, find_padrao_tag
from corrector.xml_corrector import XMLCorrector
from lxml import etree
from io import BytesIO
from urllib.parse import unquote
import os
import re
import platform
import difflib
import logging

app = Flask(__name__)

# Configurar o logger
logging.basicConfig(filename='app.log', level=logging.INFO,
                    format='%(asctime)s %(levelname)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

UPLOAD_FOLDER = 'uploads'

if platform.system() == 'Windows':
    SCHEMA_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'schemas\\')
elif platform.system() == 'Linux':
    SCHEMA_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'schemas/')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
    
# Função para corrigir o XML
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


# Função para gravar o arquivo modificado
def gravar_arquivo(xml_string, nome_arquivo):
    try:
        with open(nome_arquivo, 'w') as f:
            f.write(xml_string)
    except Exception as e:
        return str(e)

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

# Função para validar o XML contra o XSD correspondente ao TISS
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

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        arquivo = request.files['arquivo']
        if arquivo:
            # Corrigir e modificar o XML
            xml_string = corrigir_xml(arquivo)
            gravar_arquivo(xml_string, 'exemplo_original.xml')
            xml_string_modificado = XMLCorrector.modificar_xml(xml_string)
            gravar_arquivo(xml_string_modificado, 'exemplo_modificado.xml')
            
            tiss_version = find_padrao_tag('exemplo_modificado.xml')
            logging.info(f"Versao do TISS encontrada: {tiss_version}")
            
            # Identificar as linhas alteradas
            diff_lines = difflib.unified_diff(xml_string.splitlines(), xml_string_modificado.splitlines(), lineterm='')
            linhas_alteradas = [line[3:] for line in diff_lines if line.startswith('+')]
            # Redirecionar para a página de exibição do XML
            return render_template('ler_xml.html', xml_string=xml_string_modificado, linhas_alteradas=linhas_alteradas, tiss_version=tiss_version)
    return render_template('index.html')

@app.route('/validar_tiss', methods=['GET', 'POST'])
def validar_tiss():
    # Verificar se o arquivo 'exemplo_modificado.xml' existe
    if os.path.exists('exemplo_modificado.xml'):
        tiss_version = find_padrao_tag('exemplo_modificado.xml')
        xsd_path = f"{SCHEMA_FOLDER}tissV{tiss_version.replace('.', '_')}.xsd"  
        resultado = validar_xml_contra_xsd('exemplo_modificado.xml', xsd_path, tiss_version)
        
        # Renderizar a página com o resultado da validação
        return render_template('resultado_validacao.html', resultado_validacao=resultado)
    else:
        resultado = 'Nenhum arquivo XML foi encontrado para validação'
        return render_template('resultado_validacao.html', resultado_validacao=resultado)
    
    
@app.route('/corrigir_xml', methods=['GET', 'POST'])
def corrigir():
    # Corrigir e modificar o XML
    tree = etree.parse('exemplo_original.xml')
    xml_bytes = etree.tostring(tree, pretty_print=True)
    xml_string = xml_bytes.decode('utf-8')
    xml_string_modificado = XMLCorrector.modificar_xml(xml_string)

    # Identificar as linhas alteradas
    diff = difflib.unified_diff(xml_string.splitlines(), xml_string_modificado.splitlines(), lineterm='')
    linhas_alteradas = []
    linha_anterior = None
    for line in diff:
        if line.startswith('+'):
            num_linha = 0
            for i, l in enumerate(xml_string_modificado.splitlines()):
                if l == line[1:]:
                    num_linha = i + 1
                    break
            if line[1:] != linha_anterior and num_linha > 0:
                linhas_alteradas.append((num_linha, line[1:]))
                linha_anterior = line[1:]

    # Ordenar as linhas alteradas por número
    linhas_alteradas.sort(key=lambda x: x[0])

    # Remover linhas duplicadas
    linhas_unicas = []
    linhas_vistas = set()
    for num_linha, conteudo in linhas_alteradas:
        if conteudo not in linhas_vistas:
            linhas_unicas.append((num_linha, conteudo))
            linhas_vistas.add(conteudo)

    return render_template('corrigir_xml.html', linhas_alteradas=linhas_unicas, xml_string=xml_string_modificado)


@app.route('/download_xml')
def download_xml():
    try:
        arquivo_modificado = open('exemplo_modificado.xml', 'rb')
        return send_file(arquivo_modificado, as_attachment=True, mimetype='application/xml', download_name='exemplo_modificado.xml')
    except FileNotFoundError:
        return "Arquivo XML não encontrado."
    
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)