/* global $ tuskar */

tuskar.formsetTable = (function () {
    "use strict";

    var module = {};


    // go through the whole table and fix the numbering of rows
    module.reenumerateRows = function (table, prefix) {
        var count = 0;
        var inputNameRE = new RegExp("^" + prefix + "-(\\d+|__prefix__)-");
        var inputIdRE = new RegExp("^id_" + prefix + "-(\\d+|__prefix__)-");

        table.find("tbody tr").each(function () {
            $(this).find("input").each(function () {
                var input = $(this);
                input.attr("name", input.attr("name").replace(
                    inputNameRE, prefix + "-" + count + "-"));
                input.attr("id", input.attr("id").replace(
                    inputIdRE, "id_" + prefix + "-" + count + "-"));
            });
            count += 1;
        });
        $("#id_" + prefix + "-TOTAL_FORMS").val(count);
    };

    // mark a row as deleted and hide it
    module.deleteRow = function () {
        $(this).closest("tr").hide();
        $(this).prev("input[name$=\"-DELETE\"]").attr("checked", true);
    };

    // replace the "Delete" checkboxes with × for deleting rows
    module.replaceDelete = function (where) {
        where.find("input[name$=\"-DELETE\"]").hide().after(
            $("<a href=\"#\" class=\"close\">×</a>").click(module.deleteRow)
        );
    };

    // add more empty rows in the flavors table
    module.addRow = function (table, prefix, emptyRowHtml) {
        var newRow = $(emptyRowHtml);
        module.replaceDelete(newRow);
        table.find("tbody").append(newRow);
        module.reenumerateRows(table, prefix);
    };

    // prepare all the javascript for formset table
    module.init = function (prefix, emptyRowHtml, addLabel) {

        var table = $("table#" + prefix);

        module.replaceDelete(table);

        // if there are extra empty rows, add the button for new rows
        if (addLabel) {
            var button = $("<a href=\"#\" class=\"btn btn-small pull-right\">" +
                addLabel + "</a>");
            table.find("tfoot td").append(button);
            button.click(function () {
                module.addRow(table, prefix, emptyRowHtml);
            });
        }

        // if the formset is not empty and has no errors,
        // delete the empty extra rows from the end
        var initialForms = +$("#id_" + prefix + "-INITIAL_FORMS").val();
        var totalForms = +$("#id_" + prefix + "-TOTAL_FORMS").val();

        if (table.find("tbody tr").length > 1 &&
            table.find("tbody td.error").length === 0 &&
            totalForms > initialForms) {
            table.find("tbody tr").each(function (index) {
                if (index >= initialForms) {
                    $(this).remove();
                }
            });
            module.reenumerateRows(table, prefix);
            $("#id_" + prefix + "-INITIAL_FORMS").val(
                $("#id_" + prefix + "-TOTAL_FORMS").val());
        }

        // enable tooltips
        table.find("td.error[title]").tooltip();
    };

    return module;
}());
