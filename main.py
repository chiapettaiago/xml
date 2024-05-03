from flask import Flask, render_template, request, redirect, url_for, send_file
from validate import listar_versoes_tiss, validar_xml_contra_xsd, find_padrao_tag
from lxml import etree
from io import BytesIO
from urllib.parse import unquote
import os
import re

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
SCHEMA_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'schemas\\')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
    
# Função para corrigir o XML
def corrigir_xml(arquivo):
    try:
        xml_data = arquivo.read()
        parser = etree.XMLParser(recover=True)  # Permitir a recuperação de erros
        tree = etree.parse(BytesIO(xml_data), parser=parser)
        return etree.tostring(tree.getroot(), encoding='utf-8', method='xml').decode("utf-8")
    except etree.XMLSyntaxError:
        xml_data = arquivo.read()
        xml_data = xml_data.decode("utf-8")
        pos = xml_data.find('<')
        if pos > 0:
            xml_data = xml_data[pos:]
        xml_data = '<?xml version="1.0"?>' + xml_data
        return xml_data

# Função para modificar o XML
def modificar_xml(xml_string):
    try:
        root = etree.fromstring(xml_string)
        for element in root.iter():
            if element.text:
                if re.match(r'^\d+(\.\d+)?$', element.text):
                    # Verifica se o texto contém apenas números
                    if element.tag.endswith('valorUnitario') or element.tag.endswith('valorTotal') or element.tag.endswith('valorProcedimentos') or element.tag.endswith('valorTotalGeral') or element.tag.endswith('reducaoAcrescimo'):
                        # Arredonda para duas casas decimais se estiver nas tags mencionadas
                        element.text = "{:.2f}".format(float(element.text))
        return etree.tostring(root, encoding='utf-8', method='xml').decode("utf-8")
    except etree.XMLSyntaxError:
        return "Erro XML: XML inválido."


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
            xml_string_modificado = modificar_xml(xml_string)
            gravar_arquivo(xml_string_modificado, 'exemplo_modificado.xml')
            # Redirecionar para a página de exibição do XML
            return render_template('ler_xml.html', xml_string=xml_string_modificado)
    return render_template('index.html')

@app.route('/validar_tiss', methods=['GET', 'POST'])
def validar_tiss():
    if request.method == 'POST':
        arquivo = request.files['arquivo']
        if arquivo:
            # Salvar o arquivo temporariamente
            arquivo_temporario = 'temp.xml'
            arquivo.save(arquivo_temporario)
            
            # Obter o caminho do XSD correspondente à versão do TISS no XML
            xml_string = corrigir_xml(arquivo)
            tiss_version = find_padrao_tag(arquivo_temporario)
            erro_tiss = None
            if tiss_version is None:
                erro_tiss = "Não foi possível encontrar a versão do TISS"
            
            
            xsd_path = f"{SCHEMA_FOLDER}tissV{tiss_version.replace('.', '_')}.xsd"
            
            # Validar o XML contra o XSD correspondente
            resultado = validar_xml_contra_xsd(arquivo_temporario, xsd_path)
            
            # Remover o arquivo temporário
            os.remove(arquivo_temporario)
            
            # Renderizar a página com o resultado da validação
            return render_template('resultado_validacao.html', resultado_validacao=resultado, erro_tiss=erro_tiss)
    return render_template('resultado_validacao.html')



@app.route('/download_xml')
def download_xml():
    try:
        arquivo_modificado = open('exemplo_modificado.xml', 'rb')
        return send_file(arquivo_modificado, as_attachment=True, mimetype='application/xml', download_name='exemplo_modificado.xml')
    except FileNotFoundError:
        return "Arquivo XML não encontrado."
    
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
