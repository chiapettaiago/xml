// Função para acionar o download do arquivo XML modificado
function downloadXml() {
    fetch('/download_xml')
    .then(response => response.blob())
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'exemplo_modificado.xml';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
    });
}

// Chama a função downloadXml() ao carregar a página
window.onload = function() {
    downloadXml();
};