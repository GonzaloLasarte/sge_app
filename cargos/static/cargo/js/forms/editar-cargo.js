$( document ).ready(function() {

    var nivel;
    var niveles = ["Región", "Zona", "Distrito General", "Distrito", "Grupo"];
    var fields = ["region", "zona", "distrito_general", "distrito", "grupo"];
    
    //Boilerplate AJAX loading if using cookies
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    
    var csrftoken = getCookie('csrftoken');
    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });
    
    function resetElemento (nombre_elemento, reset = true) {
        var posicion= fields.indexOf(nombre_elemento);
        for (i = posicion; i < fields.length; i++) {
            var elemento = $(".field-" + fields[i])
            elemento.hide();
            $(".field-" + fields[i] + " > div > select").html('<option value="">---------</option>');
        }
        if (reset == true) {
            $(".submit-row > input").hide();
            $("#id_object_id").val('');
        }
    }

    function get_estructura(id, field, child, input) {
        $.getJSON('/getEstructura/',{id:id,field:field,child:child}, function(j){
            var options = '<option value="">---------</option>'; 
            for (var i = 0; i < j.length; i++) {
                options += '<option value="' + j[i][0]+ '">' + j[i][1] + '</option>'; 
            }
            // inspect html to check id of subcategory select dropdown.
            input.html(options); 
        }); 
    }

    $("[id$=nivel]").on('change', function(e) {
        e.preventDefault();
        resetElemento('region');
        if ($("[id$=nivel] option:selected").text().toLowerCase() == 'nacional' || $("[id$=nivel] option:selected").text().toLowerCase() == 'sin nivel') {
            $("#id_object_id").val($(this).val());
            $(".submit-row > input").show();
        } else {
            nivel = $(this).children("option:selected").html();
            $(".field-region").show();
            $.getJSON('/getRegiones/',{}, function(j){
                var options = '<option value="">---------</option>'; 
                for (var i = 0; i < j.length; i++) {
                    options += '<option value="' + j[i][0]+ '">' + j[i][1] + '</option>'; 
                } 
                // inspect html to check id of subcategory select dropdown.
                $("#id_region").html(options);
            
            });
        }
    });

    $('select.customDropDown').change(function () {
        var nombre_elemento = $(this).attr('id').replace("id_", "");
        var posicion= fields.indexOf(nombre_elemento);
        if (niveles[posicion] == nivel) {
            $("#id_object_id").val($(this).val());
            resetElemento('region', false);
            $(".submit-row > input").show();
        } else {
            var next_nivel = fields[posicion + 1];
            resetElemento(next_nivel);
            $(".field-" + next_nivel).show();
            var next_elemento = $('#id_' + next_nivel);
            get_estructura(this.value, nombre_elemento + '_id', next_nivel, next_elemento);
        }
    });

    $("#id_object_id").prop( "readonly", true );
    resetElemento('region', false);
});
