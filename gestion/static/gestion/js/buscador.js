$("#buscador").keyup(function () {
    var busq = $(this).val();
    $.each($(".filtro"), function (i, str) {
        var cadena = $(this).children().first().text() + ' ';
        var cadena = cadena + $(this).children().first().next().text() + ' ';
        var cadena = cadena + $(this).children().first().next().next().text();
        if (busq.length == 0) {
            $(this).removeClass('collapse');
        } else {
            if (cadena.search(RegExp(busq, "i")) >= 0) {
                $(this).removeClass('collapse')
            } else {
                $(this).addClass('collapse')
            };
        };


    })
});