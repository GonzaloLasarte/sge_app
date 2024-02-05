$( document ).ready(function() {
    
    function today() {
        var now = new Date();
        var day = ("0" + now.getDate()).slice(-2);
        var month = ("0" + (now.getMonth() + 1)).slice(-2);

        return now.getFullYear()+"-"+(month)+"-"+(day) ;
    }

    $("#date").val(today());

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

    $.getJSON('/getMotivosBaja/', function(j){
        var options = '<option value="">---------</option>'; 
        for (var i = 0; i < j.length; i++) {
            options += '<option value="' + j[i][0]+ '">' + j[i][1] + '</option>'; 
        }
        $("#motivosBaja").html(options);
    });

    var traslado = 'Por traslado a otro país';

    $("#motivosBaja").on('change', function() {
        motivo = $(this).val();
        if (motivo == traslado) {
            $('#pDestino').show();
        } else {
            $('#pDestino').hide();
            $('#destino').val('');
        }
    });
    

});