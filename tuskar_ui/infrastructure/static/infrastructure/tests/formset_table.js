/* global $ horizon tuskar module test equal */
horizon.addInitFunction(function () {
    "use strict";

    module("Formset table (tuskar.formset_table.js)");

    test("Reenumerate rows", function () {
        var html = $("#qunit-fixture");
        var table = html.find("table");
        var input = table.find("tbody tr#flavors__row__14 input").first();

        input.attr("id", "id_flavors-3-name");
        tuskar.formsetTable.reenumerateRows(table, "flavors");
        equal(input.attr("id"), "id_flavors-0-name", "Enumerate old rows ids");
        input.attr("id", "id_flavors-__prefix__-name");
        tuskar.formsetTable.reenumerateRows(table, "flavors");
        equal(input.attr("id"), "id_flavors-0-name", "Enumerate new rows ids");
    });

    test("Delete row", function () {
        var html = $("#qunit-fixture");
        var table = html.find("table");
        var row = table.find("tbody tr").first();
        var input = row.find("input#id_flavors-0-DELETE");

        equal(row.css("display"), "table-row");
        equal(input.attr("checked"), undefined);
        tuskar.formsetTable.replaceDelete(row);
        var x = input.next("a");
        tuskar.formsetTable.deleteRow.call(x);
        equal(row.css("display"), "none");
        equal(input.attr("checked"), "checked");
    });

    test("Add row", function() {
        var html = $("#qunit-fixture");
        var table = html.find("table");
        var emptyRowHtml = "<tr><td><input id=\"id_flavors-__prefix__-name\" name=\"flavors-__prefix__-name\"></td></tr>";

        equal(table.find("tbody tr").length, 3);
        equal(html.find("#id_flavors-TOTAL_FORMS").val(), 3);
        tuskar.formsetTable.add_row(table, "flavors", emptyRowHtml);
        equal(table.find("tbody tr").length, 4);
        equal(table.find("tbody tr:last input").attr("id"), "id_flavors-3-name");
        equal(html.find("#id_flavors-TOTAL_FORMS").val(), 4);
    });

    test("Init formset table", function() {
        var html = $("#qunit-fixture");
        var table = html.find("table");

        tuskar.formsetTable.init("flavors", "", "Add row");
        equal(table.find("tfoot tr a").html(), "Add row");
    });

    test("Init formset table -- no add", function() {
        var html = $("#qunit-fixture");
        var table = html.find("table");

        tuskar.formsetTable.init("flavors", "", "");
        equal(table.find("tfoot tr a").length, 0);
    });
});
