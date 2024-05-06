// Adicionando o comportamento de opacidade ao rolar a página
window.onscroll = function() {scrollFunction()};

function scrollFunction() {
    if (document.body.scrollTop > 50 || document.documentElement.scrollTop > 50) {
        document.querySelector('.navbar').style.opacity = '0.8';
    } else {
        document.querySelector('.navbar').style.opacity = '1';
    }
}