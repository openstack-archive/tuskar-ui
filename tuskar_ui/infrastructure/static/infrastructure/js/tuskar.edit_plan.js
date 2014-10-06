tuskar.edit_plan = (function () {
    'use strict';

    var module = {};

    module.debounce_timer = null;

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
        $('div.deployment-box ul').replaceWith(
            module.message_template.render(data));
        if (data === null) {
            $('div.deployment-buttons a.btn-primary').addClass('disabled');
            $('div.deployment-icon i').replaceWith(
                '<i class="fa fa-spinner fa-spin text-info"></i>');
        } else if (data.plan_invalid) {
            $('div.deployment-buttons a.btn-primary').addClass('disabled');
            $('div.deployment-icon i').replaceWith(
                '<i class="fa fa-exclamation-circle text-danger"></i>');
            $('div.deployment-box h4').replaceWith(
                module.title_template.render(data));
        } else {
            $('div.deploymnet-buttons a.btn-primary').removeClass('disabled');
            $('div.deployment-icon i').replaceWith(
                '<i class="fa fa-check-circle text-success"></i>');
            $('div.deployment-box h4').replaceWith(
                module.title_template.render(data));
        }
    };

    horizon.addInitFunction(module.init);
    return module;
} ());
