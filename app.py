from controllers.main_controller import index, validar_tiss, corrigir, download_xml, version
from controllers.tiss_controller import SCHEMA_FOLDER
import logging
import os
from flask import Flask

app = Flask(__name__, template_folder='views/templates')

# Configurar o logger
logging.basicConfig(filename='app.log', level=logging.INFO,
                    format='%(asctime)s %(levelname)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

UPLOAD_FOLDER = 'uploads'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.route('/', methods=['GET', 'POST'])(index)
app.route('/validar_tiss', methods=['GET', 'POST'])(validar_tiss)
app.route('/corrigir_xml', methods=['GET', 'POST'])(corrigir)
app.route('/download_xml')(download_xml)
app.route('/version')(version)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)