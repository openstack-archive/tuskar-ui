tuskar.formset_table = (function () {
    'use strict';

    var module = {};


    // go through the whole table and fix the numbering of rows
    module.reenumerate_rows = function (table, prefix) {
        var count = 0;
        var input_name_re = new RegExp('^' + prefix + '-(\\d+|__prefix__)-');
        var input_id_re = new RegExp('^id_' + prefix + '-(\\d+|__prefix__)-');

        table.find('tbody tr').each(function () {
            $(this).find('input').each(function () {
                var input = $(this);
                input.attr('name', input.attr('name').replace(
                    input_name_re, prefix + '-' + count + '-'));
                input.attr('id', input.attr('id').replace(
                    input_id_re, 'id_' + prefix + '-' + count + '-'));
            });
            count += 1;
        });
        $('#id_' + prefix + '-TOTAL_FORMS').val(count);
    };

    // mark a row as deleted and hide it
    module.delete_row = function (e) {
        $(this).closest('tr').hide();
        $(this).prev('input[name$="-DELETE"]').attr('checked', true);
    };

    // replace the "Delete" checkboxes with × for deleting rows
    module.replace_delete = function (where) {
        where.find('input[name$="-DELETE"]').hide().after(
            $('<a href="#" class="close">×</a>').click(module.delete_row)
        );
    };

    // add more empty rows in the flavors table
    module.add_row = function (table, prefix, empty_row_html) {
        var new_row = $(empty_row_html);
        module.replace_delete(new_row);
        table.find('tbody').append(new_row);
        module.reenumerate_rows(table, prefix);
    };

    // prepare all the javascript for formset table
    module.init = function (prefix, empty_row_html, add_label) {

        var table = $('table#' + prefix);

        module.replace_delete(table);

        // if there are extra empty rows, add the button for new rows
        if ($('#id_' + prefix + '-TOTAL_FORMS').val() >
                $('#id_' + prefix + '-INITIAL_FORMS').val()) {
            var button = $('<a href="#" class="btn btn-small pull-right">' +
                           add_label + '</a>');
            table.find('tfoot td:last').append(button);
            button.click(function () {
                module.add_row(table, prefix, empty_row_html);
            });
        };

        // if the formset is not empty, and is not being redisplayed,
        // delete the empty extra row from the end
        if (table.find('tbody tr').length > 1 &&
                $('#id_' + prefix + '-TOTAL_FORMS').val() >
                    $('#id_' + prefix + '-INITIAL_FORMS').val()) {
            table.find('tbody tr:last').remove();
            module.reenumerate_rows(table, prefix);
            $('#id_' + prefix + '-INITIAL_FORMS').val(
                $('#id_' + prefix + '-TOTAL_FORMS').val());
        };
    };

    return module;
} ());
