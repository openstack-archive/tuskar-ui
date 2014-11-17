tuskar.deployment_progress = (function () {
  'use strict';

  var module = {};

  module.init = function () {
    var that = this;
    if (!$('div.deployment-box div.progress').length) { return; }
    this.interval = setInterval(function () {
      that.check_progress();
    }, 30000);
    this.events_template = Hogan.compile($('#events-template').html() || '');
    this.roles_template = Hogan.compile($('#roles-template').html() || '');
  };

  module.check_progress = function () {
    var $form = $('form.deployment-roles-form');
    $.ajax({
      type: 'GET',
      headers: {'X-Horizon-Progress': 'true'},
      url: $form.attr('action'),
      dataType: 'json',
      async: true,
      success: this.update_progress
    });
  };

  module.update_progress = function (data) {
    if (data.progress >= 100 || data.progress <= 0) {
      window.location.reload(true);
    }
    var $bar = $('div.deployment-box div.progress div.progress-bar');
    $bar.css('width', '' + data.progress + '%');
    if (data.last_failed_events.length > 0 || data.last_event) {
      $('div.deploy-last-events').html(this.events_template.render(data));
    } else {
      $('div.deploy-last-events').html('');
    }
    $('div.deploy-role-status').html(this.roles_template.render(data));
  };

  horizon.addInitFunction(module.init);
  return module;
} ());
