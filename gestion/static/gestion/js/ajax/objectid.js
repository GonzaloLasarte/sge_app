$( document ).ready(function() {
    $(function(){
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

        //Prepopulate object_id
        var cargo_rows, nivel, member_id, options, order_id;
        cargo_rows = $("tr[id^='cargo_set-']").not('[id$="empty"]');;
        var pathname = String(window.location.pathname);
        member_id = pathname.split('/')[4];

        for (var i=0; i<cargo_rows.length; i++) {
            nivel_id = $("#id_cargo_set-" + i + "-nivel").val();
            $.getJSON("/get_object_id/",{member_id: member_id, order_id: i, nivel_id: nivel_id}, function(j) {
                options = '<option value="' + parseInt(j['pk']) + '">' + j['text'] + '</option>';
                $("#id_cargo_set-" + j['order_id'] + "-object_id").html(options);
            });
        }

        //Code that does the filtering
        $("[id$=nivel]").on('change', function(e) {
            e.preventDefault();
            var trid = $(this).closest('tr').index();
            var object_id = $("#id_cargo_set-" + trid + "-object_id");
            $.getJSON("/populate_object_id/",{id: $(this).val()}, function(j) {
                var options = '<option value="">--------</option>';
                for (var i = 0; i < j.length; i++) {
                    options += '<option value="' + parseInt(j[i][0]) + '">' + j[i][1] + '</option>';
                }
                $("#id_cargo_set-" + trid + "-object_id").html(options);
            });
        });
    });
});
