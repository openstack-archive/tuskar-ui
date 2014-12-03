/* global $ horizon tuskar Hogan window */
tuskar.editPlan = (function () {
    "use strict";

    var module = {};

    module.debounceTimer = null;
    module.ICON_CLASSES = (
	"fa-spinner " +
	"fa-spin " +
	"fa-cloud " +
	"fa-exclamation-circle " +
	"fa-check-circle " +
	""
    );

    module.init = function () {
        if (!$("form.deployment-roles-form").length) { return; }
        // Attach event listeners and hide the submit button.
        $("form.deployment-roles-form input.number-picker"
            ).change(module.onChange);
        $("form.deployment-roles-form [type=submit]").hide();
        // Compile the templates.
        module.messageTemplate = Hogan.compile(
            $("#message-template").html() || "");
        module.titleTemplate = Hogan.compile(
            $("#title-template").html() || "");
    };

    module.onChange = function () {
        // Only save when there was no activity for half a second.
        window.clearTimeout(module.debounceTimer);
        module.debounceTimer = window.setTimeout(module.saveForm, 500);
    };

    module.saveForm = function () {
        // Save the current plan and get validation results.
        var $form = $("form.deployment-roles-form");
        module.updateMessages(null);
        $.ajax({
          type: "POST",
          headers: {"X-Horizon-Validate": "true"},
          url: $form.attr("action"),
          data: $form.serialize(),
          dataType: "json",
          async: true,
          success: module.updateMessages
        });
    };

    module.updateMessages = function (data) {
        if (data === null) {
            $("div.deployment-buttons a.btn-primary").addClass("disabled");
            $("div.deployment-icon i").removeClass(module.ICON_CLASSES
		).addClass("fa-spinner fa-spin");
            data = {validating: true};
        } else if (data.plan_invalid) {
            $("div.deployment-buttons a.btn-primary").addClass("disabled");
            $("div.deployment-icon i").removeClass(module.ICON_CLASSES
		).addClass("fa-exclamation-circle");
        } else {
            $("div.deployment-buttons a.btn-primary").removeClass("disabled");
            $("div.deployment-icon i").removeClass(module.ICON_CLASSES
		).addClass("fa-check-circle");
        }
        $("div.deployment-box h4").replaceWith(
            module.titleTemplate.render(data));
        $("div.deployment-box ul").replaceWith(
            module.messageTemplate.render(data));
    };

    horizon.addInitFunction(module.init);
    return module;
}());
