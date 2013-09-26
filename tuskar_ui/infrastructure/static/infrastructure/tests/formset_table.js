horizon.addInitFunction(function () {
    module("Formset table (tuskar.formset_table.js)");

    test("Reenumerate rows", function () {
        var table = $('<table><tbody>' +
            '<tr id="table__row__1">' + 
            '   <td><input type="text" id="id_table-1-name" name="table-1-name"></td>' + 
            '   <td><input type="hidden" id="id_table-1-id" name="table-1-id"></td>' +
            '</tr>' +
            '<tr id="table__row____prefix__">' +
            '   <td><input type="text" id="id_table-__prefix__-name" name="table-__prefix__-name"></td>' + 
            '   <td><input type="hidden" id="id_table-__prefix__-id" name="table-__prefix__-id"></td>' +
            '</tr>' +
            '</tbody></table>'
        );

        tuskar.formset_table.reenumerate_rows(table, 'table');

        equal(table.find('tr#table__row__1 input[type="text"]').attr('id'),
            'id_table-0-name', 
            "Enumerate old rows ids");
        equal(table.find('tr#table__row____prefix__ input[type="text"]').attr('id'),
            'id_table-1-name', 
            "Enumerate new rows ids");
        equal(table.find('tr#table__row__1 input[type="text"]').attr('name'),
            'table-0-name', 
            "Enumerate old rows names");
        equal(table.find('tr#table__row____prefix__ input[type="text"]').attr('name'),
            'table-1-name', 
            "Enumerate new rows names");
    });
});
