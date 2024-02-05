$(document).ready(function(){
    $('#messages').on('click', function(event){
        event.stopPropagation();
    });

    $('.closediv').on('click', function(){
        var id = this.id;
        Sijax.request('verNotificacion', [
                        id
                    ]);
    });

    // $('#datatables').DataTable({
    //     "pagingType": "simple",
    //     "lengthMenu": [[20, 40, 50, -1], [20, 40, 50, "Todos"]],
    //     responsive: true,
    //     language: {
    //         "sProcessing": "Procesando...",
    //         "sLengthMenu": "Mostrar _MENU_ registros",
    //         "sZeroRecords": "No se encontraron resultados",
    //         "sEmptyTable": "Ningún dato disponible en esta tabla",
    //         "sInfo": "Registros _START_ al _END_ de _TOTAL_",
    //         "sInfoEmpty": "Registros 0 al 0 de 0",
    //         "sInfoFiltered": "(filtrado)",
    //         "sInfoPostFix": "",
    //         "sSearch": "Buscar",
    //         "sUrl": "",
    //         "sInfoThousands": ".",
    //         "sLoadingRecords": "Cargando...",
    //         "oPaginate": {
    //             "sFirst": "Primero",
    //             "sLast": "Último",
    //             "sNext": "Siguiente",
    //             "sPrevious": "Anterior"
    //         },
    //         "oAria": {
    //             "sSortAscending": ": Activar para ordenar la columna de manera ascendente",
    //             "sSortDescending": ": Activar para ordenar la columna de manera descendente"
    //         }
    //     }
    // });

    //De jQuery.dropdown para inicializar los select
    $(".select").dropdown({ "autoinit": ".select" });

    //Creamos una llamada AJAX cuando ha terminado de cargar para popular los datos de desplegables
    Sijax.request('LlenaDesplegables');

});