from flask import Flask, render_template, request,send_file
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from controllers.xml_controller import corrigir_xml, contar_guias, extrair_numero_lote, extrair_valor_total, gravar_arquivo, tipo_guia
from controllers.tiss_controller import SCHEMA_FOLDER
from controllers.validation_controller import validar_xml_contra_xsd, find_padrao_tag, find_operadora, find_transacao
from models.xml_corrector import XMLParameters
from lxml import etree
from controllers.xml_controller import find_padrao_tag
import difflib
import logging

app = Flask(__name__)

# Configurar o logger
logging.basicConfig(filename='app.log', level=logging.INFO,
                    format='%(asctime)s %(levelname)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

UPLOAD_FOLDER = 'uploads'
ORIGINAL_XML_FOLDER = 'uploads/original_xml'
MODIFIED_XML_FOLDER = 'uploads/modified_xml'


app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ORIGINAL_XML_FOLDER'] = ORIGINAL_XML_FOLDER
app.config['MODIFIED_XML_FOLDER'] = MODIFIED_XML_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
    
def index():
    if request.method == 'POST':
        arquivo = request.files['arquivo']
        if arquivo:
            # Corrigir e modificar o XML
            xml_string = corrigir_xml(arquivo)
            gravar_arquivo(xml_string, os.path.join(ORIGINAL_XML_FOLDER, 'exemplo_original.xml'))
            xml_string_modificado = XMLParameters.modificar_xml(xml_string)
            gravar_arquivo(xml_string_modificado, os.path.join(MODIFIED_XML_FOLDER, 'exemplo_modificado.xml'))
            
            tiss_version = find_padrao_tag(os.path.join(MODIFIED_XML_FOLDER, 'exemplo_modificado.xml'))
            logging.info(f"Versao do TISS encontrada: {tiss_version}")
            
            num_guias = contar_guias(os.path.join(MODIFIED_XML_FOLDER, 'exemplo_modificado.xml'))
            
            numero_lote = extrair_numero_lote(os.path.join(MODIFIED_XML_FOLDER, 'exemplo_modificado.xml'))
            
            valor_total = extrair_valor_total(os.path.join(MODIFIED_XML_FOLDER, 'exemplo_modificado.xml'))
            
            valor_total_modificado = round(valor_total, 2)
            
            operadora = find_operadora(os.path.join(MODIFIED_XML_FOLDER, 'exemplo_modificado.xml'))
            
            transacao = find_transacao(os.path.join(MODIFIED_XML_FOLDER, 'exemplo_modificado.xml'))

            tipo_de_guia = tipo_guia(os.path.join(MODIFIED_XML_FOLDER, 'exemplo_modificado.xml'))
                
            # Identificar as linhas alteradas
            diff_lines = difflib.unified_diff(xml_string.splitlines(), xml_string_modificado.splitlines(), lineterm='')
            linhas_alteradas = [line[3:] for line in diff_lines if line.startswith('+')]
            # Redirecionar para a página de exibição do XML
            return render_template('ler_xml.html', xml_string=xml_string_modificado, linhas_alteradas=linhas_alteradas, tipo_de_guia=tipo_de_guia, num_guias=num_guias, valor_total=valor_total_modificado, numero_lote=numero_lote, tiss_version=tiss_version, operadora=operadora, transacao=transacao)
    return render_template('index.html')

def validar_tiss():
    # Verificar se o arquivo 'exemplo_modificado.xml' existe
    if os.path.exists(os.path.join(MODIFIED_XML_FOLDER, 'exemplo_modificado.xml')):
        tiss_version = find_padrao_tag(os.path.join(MODIFIED_XML_FOLDER, 'exemplo_modificado.xml'))
        xsd_path = f"{SCHEMA_FOLDER}tissV{tiss_version.replace('.', '_')}.xsd"  
        resultado = validar_xml_contra_xsd(os.path.join(MODIFIED_XML_FOLDER, 'exemplo_modificado.xml'), xsd_path, tiss_version)
        
        # Renderizar a página com o resultado da validação
        return render_template('resultado_validacao.html', resultado_validacao=resultado)
    else:
        resultado = 'Nenhum arquivo XML foi encontrado para validação'
        return render_template('resultado_validacao.html', resultado_validacao=resultado)
    
def corrigir():
    # Corrigir e modificar o XML
    tree = etree.parse(os.path.join(ORIGINAL_XML_FOLDER, 'exemplo_original.xml'))
    xml_bytes = etree.tostring(tree, pretty_print=True)
    xml_string = xml_bytes.decode('utf-8')
    xml_string_modificado = XMLParameters.modificar_xml(xml_string)

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

def download_xml():
    try:
        arquivo_modificado = os.path.join(MODIFIED_XML_FOLDER, 'exemplo_modificado.xml')
        if os.path.exists(arquivo_modificado):
            return send_file(arquivo_modificado, as_attachment=True, mimetype='application/xml', download_name='exemplo_modificado.xml')
        else:
            return "Arquivo XML não encontrado."
    except (FileNotFoundError, IOError, OSError) as e:
        return f"Erro ao baixar o arquivo XML: {str(e)}"
    
def version():
    return render_template('versao.html')