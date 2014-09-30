tuskar.edit_plan = (function () {
    'use strict';

    var module = {};

    module.debounce_timer = null;
    module.template = Hogan.compile(
        '<ul class="list-unstyled">' +
        '{{#messages }}' +
        '  <li class="' +
        '    {{#is_critical}}text-danger{{/is_critical}}' +
        '    {{^is_critical}}text-warning{{/is_critical}}' +
        '  "><p>' +
        '    {{text}}' +
        '    {{#link_label}}' +
        '      <a href="{{link_url}}">' +
        '        {{link_label}}' +
        '      </a>' +
        '    {{/link_label}}' +
        '  </p></li>' +
        '{{/messages}}' +
        '</ul>'
    );

    module.init = function () {
        // Attach event listeners and hide the submit button.
        $('form.deployment-roles-form input.number-picker'
            ).change(module.on_change);
        $('form.deployment-roles-form [type=submit]').hide();
    };

    module.on_change = function () {
        // Only save when there was no activity for half a second.
        window.clearTimeout(module.debounce_timer);
        module.debounce_timer = window.setTimeout(module.save_form, 500);
    };

    module.save_form = function () {
        // Save the current plan and get validation results.
        var $form = $('form.deployment-roles-form');
        model.update_messages([]);
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
        $('div.deployment-box ul').replaceWith(module.template.render(data));
        if (!data) {
            $('div.deployment-buttons a.btn-primary').addClass('disabled');
            $('div.deployment-icon i').replaceWith(
                '<i class="fa fa-spinner fa-spin text-info"></i>');
        } else if (data.plan_invalid) {
            $('div.deployment-buttons a.btn-primary').addClass('disabled');
            $('div.deployment-icon i').replaceWith(
                '<i class="fa fa-exclamation-circle text-danger"></i>');
            $('div.deployment-box h4').text(_('Design your deploymnet'));
        } else {
            $('div.deploymnet-buttons a.btn-primary').removeClass('disabled');
            $('div.deployment-icon i').replaceWith(
                '<i class="fa fa-check-circle text-success"></i>');
            $('div.deployment-box h4').text(_('Ready to get deployed'));
        }
    };

    horizon.addInitFunction(module.init);
    return module;
} ());
