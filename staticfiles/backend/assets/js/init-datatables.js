
$(document).ready( function() {
    'use strict';
    $('.convert-data-table').dataTable({
        /* No ordering applied by DataTables during initialisation */
        "order": [],
        "bDestroy": true
    });
})



function format(d) {
    // `d` is the original data object for the row
    return '<table cellpadding="5" cellspacing="0" border="0" style="padding-left:50px;">' +
        '<tr>' +
        '<td>Full name:</td>' +
        '<td>' + d.name + '</td>' +
        '</tr>' +
        '<tr>' +
        '<td>Extension number:</td>' +
        '<td>' + d.extn + '</td>' +
        '</tr>' +
        '<tr>' +
        '<td>Extra info:</td>' +
        '<td>And any further details here (images etc)...</td>' +
        '</tr>' +
        '</table>';
}


// Data Table
//
// $(document).ready(function() {
//     $('.convert-data-table').DataTable( {
//         "order": false
//     } );
// } );

$('.convert-data-table').DataTable({
    "PaginationType": "bootstrap",
    dom: '<"tbl-head clearfix"T>,<"tbl-top clearfix"lfr>,t,<"tbl-footer clearfix"<"tbl-info pull-left"i><"tbl-pagin pull-right"p>>',
    tableTools: {
        "sSwfPath": "swf/copy_csv_xls_pdf.swf",
    "bSort" : false
    }
});




$('.colvis-data-table').DataTable({
    "PaginationType": "bootstrap",
    "bSort" : false,
    dom: '<"tbl-head clearfix"C>,<"tbl-top clearfix"lfr>,t,<"tbl-footer clearfix"<"tbl-info pull-left"i><"tbl-pagin pull-right"p>>'


});


$('.responsive-data-table').DataTable({
    "PaginationType": "bootstrap",
    responsive: true,
    "bSort" : false,
    dom: '<"tbl-top clearfix"lfr>,t,<"tbl-footer clearfix"<"tbl-info pull-left"i><"tbl-pagin pull-right"p>>'
});


