from flask import Flask, render_template, request, redirect, url_for, send_file
from lxml import etree
from io import BytesIO
from urllib.parse import unquote
import os
import re

app = Flask(__name__)


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

def modificar_xml(xml_string):
    try:
        root = etree.fromstring(xml_string)
        for element in root.iter():
            if element.text:
                if re.match(r'^\d+(\.\d+)?$', element.text):
                    # Verifica se o texto contém apenas números
                    if len(element.text.split('.')) > 1:
                        # Se houver um ponto decimal, arredonda para duas casas decimais
                        element.text = "{:.2f}".format(float(element.text))
        return etree.tostring(root, encoding='utf-8', method='xml').decode("utf-8")
    except etree.XMLSyntaxError:
        return "Erro XML: XML inválido."

def gravar_arquivo(xml_string, nome_arquivo):
    try:
        with open(nome_arquivo, 'w') as f:
            f.write(xml_string)
    except Exception as e:
        return str(e)

@app.route('/', methods=['GET', 'POST'])
def ler_xml():
    mensagem = None
    if request.method == 'POST':
        arquivo = request.files['arquivo']
        if arquivo:
            xml_string = corrigir_xml(arquivo)
            xml_string_modificado = modificar_xml(xml_string)
            gravar_arquivo(xml_string_modificado, 'exemplo_modificado.xml')
            return render_template('ler_xml.html', xml_string=xml_string_modificado)
    return render_template('index.html', mensagem=mensagem)

@app.route('/download_xml')
def download_xml():
    try:
        arquivo_modificado = open('exemplo_modificado.xml', 'rb')
        return send_file(arquivo_modificado, as_attachment=True)
    except FileNotFoundError:
        return "Arquivo XML não encontrado."
    
    
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
