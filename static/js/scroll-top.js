$(document).ready(function(){
    // Mostrar/esconder o botão
    $(window).scroll(function(){
        if ($(this).scrollTop() > 100) {
            $('#btnVoltarTopoContainer').fadeIn();
        } else {
            $('#btnVoltarTopoContainer').fadeOut();
        }
    });

    // Rolagem suave ao clicar no botão
    $('#btnVoltarTopo').click(function(){
        $('html, body').animate({scrollTop : 0},800);
        return false;
    });
});