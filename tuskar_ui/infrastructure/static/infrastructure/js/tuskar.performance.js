tuskar.performance = (function () {
  'use strict';

  var module = {};

  module.show_hide_datepickers = function () {
    var date_options = $("#date_options");
    date_options.change(function(evt) {
      if ($(this).find("option:selected").val() === "other"){
        evt.stopPropagation();
        $("#date_from, #date_to").val('');
        $("#date_from_group, #date_to_group").show();
      } else {
        $("#date_from_group, #date_to_group").hide();
      }
    });
    if (date_options.find("option:selected").val() === "other"){
      $("#date_from_group, #date_to_group").show();
    } else {
      $("#date_from_group, #date_to_group").hide();
    }
  };

  return module;
} ());
