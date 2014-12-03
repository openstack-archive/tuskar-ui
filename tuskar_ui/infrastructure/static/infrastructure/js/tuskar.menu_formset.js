/* global $ horizon tuskar window */
/* eslint no-use-before-define: [1, "nofunc"] */

tuskar.menuFormset = (function () {
  "use strict";

  var module = {};

  module.init = function (prefix, emptyFormHtml) {
    var inputNameRE = new RegExp("^" + prefix + "-(\\d+|__prefix__)-");
    var inputIdRE = new RegExp("^id_" + prefix + "-(\\d+|__prefix__)-");
    var $content = $("#formset-" + prefix + " .tab-content");
    var $nav = $("#formset-" + prefix + " .nav");
    var activated = false;

    function renumberForm($form, prefix, count) {
      $form.find("input, textarea, select").each(function () {
        var input = $(this);
        input.attr("name", input.attr("name").replace(
          inputNameRE, prefix + "-" + count + "-"));
        input.attr("id", input.attr("id").replace(
          inputIdRE, "id_" + prefix + "-" + count + "-"));
      });
    }

    function reenumerateForms($forms, prefix) {
      var count = 0;
      $forms.each(function () {
        renumberForm($(this), prefix, count);
        count += 1;
      });
      $("#id_" + prefix + "-TOTAL_FORMS").val(count);
      return count;
    }

    function addDeleteLink($navItem) {
      var $form = $content.find($navItem.find("a").attr("href"));
      $navItem.prepend("<span class=\"btn-small pull-right delete-icon\"><i class=\"fa fa-times\"></i></span>");
      $navItem.find("span.delete-icon:first").click(function () {
          var count;
          $form.remove();
          $navItem.remove();
          count = reenumerateForms($content.find(".tab-pane"), prefix);
          if (count === 0) { addNode(); }
      });
    }

    function addNode() {
      var $newForm = $(emptyFormHtml);
      var count, id, $newNav;
      $content.append($newForm);
      $newForm = $content.find(".tab-pane:last");
      count = reenumerateForms($content.find(".tab-pane"), prefix);
      id = "tab-" + prefix + "-" + count;
      $newForm.attr("id", id);
      $nav.append("<li><a href=\"#" + id + "\" data-toggle=\"tab\">Undefined node</a></li>");
      $newNav = $nav.find("li > a:last");
      addDeleteLink($newNav.parent());
      $newNav.click(function () {
        $(this).tab("show");
        $("select.switchable").trigger("change");
      });
      $newNav.tab("show");
      $("select.switchable").trigger("change");
      horizon.forms.add_password_fields_reveal_buttons($newForm);
    }

    // Connect all signals.
    $("a.add-node-link").click(addNode);
    $nav.find("li").each(function () {
      addDeleteLink($(this));
    });
    $nav.find("li a").click(function () {
      window.setTimeout(function () {
        $("select.switchable").trigger("change");
      }, 0);
    });

    // Activate the first field that has errors.
    $content.find(".control-group.error").each(function () {
      if (!activated) {
        $nav.find("a[href=\"#" + $(this).closest(".tab-pane").attr("id") + "\"]").tab("show");
        activated = true;
      }
    });

  };

  return module;
}());
