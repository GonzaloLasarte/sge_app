$( document ).ready(function() {
    
    const inputOrigen = $("#id_altamiembro_set-0-origen");
    const groupFechaLlegada = $(".field-fecha_llegada_extranjero");
    const inputFechaLlegada = $("#id_altamiembro_set-0-fecha_llegada_extranjero");
    

    function resetElementosExtranjero () {
        
        inputOrigen.hide();
        inputOrigen.val("");
    
        groupFechaLlegada.hide();
        inputFechaLlegada.val("");
    
    }

    idSelectMotivo = "#id_altamiembro_set-0-motivo"
    $(idSelectMotivo).on('change', function(e) {
        e.preventDefault();
        resetElementosExtranjero();
        if ($(idSelectMotivo + " option:selected").text().toLowerCase() == 'llegada desde el extranjero') {
            inputOrigen.show()
            groupFechaLlegada.show()
        } else {
            resetElementosExtranjero()
        }
    });

    resetElementosExtranjero();

});
