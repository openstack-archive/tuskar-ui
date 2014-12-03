/* global $ horizon tuskar Hogan window setInterval */
tuskar.deploymentProgress = (function () {
  "use strict";

  var module = {};

  module.init = function () {
    if (!$("div.deployment-box div.progress").length) { return; }
    this.interval = setInterval(function () {
      module.checkProgress();
    }, 30000);
    module.eventsTemplate = Hogan.compile($("#events-template").html() || "");
    module.rolesTemplate = Hogan.compile($("#roles-template").html() || "");
  };

  module.checkProgress = function () {
    var $form = $("form.deployment-roles-form");
    $.ajax({
      type: "GET",
      headers: {"X-Horizon-Progress": "true"},
      url: $form.attr("action"),
      dataType: "json",
      async: true,
      success: this.updateProgress
    });
  };

  module.updateProgress = function (data) {
    if (data.progress >= 100 || data.progress <= 0) {
      window.location.reload(true);
    }
    var $bar = $("div.deployment-box div.progress div.progress-bar");
    $bar.css("width", "" + data.progress + "%");
    if (data.last_failed_events.length > 0 || data.last_event) {
      $("div.deploy-last-events").html(module.eventsTemplate.render(data));
    } else {
      $("div.deploy-last-events").html("");
    }
    $("div.deploy-role-status").html(module.rolesTemplate.render(data));
  };

  horizon.addInitFunction(module.init);
  return module;
}());
