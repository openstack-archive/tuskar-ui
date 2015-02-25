tuskar.edit_plan = (function () {
    'use strict';

    var module = {};

    module.debounce_timer = null;
    module.ICON_CLASSES = (
	'fa-spinner ' + 
	'fa-spin ' +
	'fa-cloud ' +
	'fa-exclamation-circle ' +
	'fa-check-circle ' +
	''
    );

    module.init = function () {
        if (!$('form.deployment-roles-form').length) { return; }
        // Attach event listeners and hide the submit button.
        $('form.deployment-roles-form input.number-picker'
            ).change(module.on_change);
        $('form.deployment-roles-form [type=submit]').hide();
        // Compile the templates.
        module.message_template = Hogan.compile(
            $('#message-template').html() || '');
        module.title_template = Hogan.compile(
            $('#title-template').html() || '');
    };

    module.on_change = function () {
        // Only save when there was no activity for half a second.
        window.clearTimeout(module.debounce_timer);
        module.debounce_timer = window.setTimeout(module.save_form, 500);
    };

    module.save_form = function () {
        // Save the current plan and get validation results.
        var $form = $('form.deployment-roles-form');
        module.update_messages(null);
        $.ajax({
          type: 'POST',
          headers: {'X-Horizon-Validate': 'true'},
          url: $form.attr('action'),
          data: $form.serialize(),
          dataType: 'json',
          async: true,
          success: module.update_messages,
        });
    };

    module.update_messages = function (data) {
        if (data === null) {
            $('div.deployment-buttons a.btn-primary').addClass('disabled');
            $('div.deployment-icon i').removeClass(module.ICON_CLASSES
		).addClass('fa-spinner fa-spin');
            data = {validating:true};
        } else if (data.plan_invalid) {
            $('div.deployment-buttons a.btn-primary').addClass('disabled');
            $('div.deployment-icon i').removeClass(module.ICON_CLASSES
		).addClass('fa-exclamation-circle');
        } else {
            $('div.deployment-buttons a.btn-primary').removeClass('disabled');
            $('div.deployment-icon i').removeClass(module.ICON_CLASSES
		).addClass('fa-check-circle');
        }
        $('div.deployment-box h4').replaceWith(
            module.title_template.render(data));
        $('div.deployment-box ul').replaceWith(
            module.message_template.render(data));
        $('div.deployment-box a#collapse-steps').text(data.steps_message);
    };

    horizon.addInitFunction(module.init);
    return module;
} ());
