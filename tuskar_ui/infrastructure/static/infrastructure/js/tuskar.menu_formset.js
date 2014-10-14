tuskar.menu_formset = (function () {
  'use strict';

  var module = {};

  module.init = function (prefix, empty_form_html) {
    var input_name_re = new RegExp('^' + prefix + '-(\\d+|__prefix__)-');
    var input_id_re = new RegExp('^id_' + prefix + '-(\\d+|__prefix__)-');
    var $content = $('#formset-' + prefix +' .tab-content');
    var $nav = $('#formset-' + prefix + ' .nav');
    var activated = false;

    function renumber_form($form, prefix, count) {
      $form.find('input, textarea, select').each(function () {
        var input = $(this);
        input.attr('name', input.attr('name').replace(
          input_name_re, prefix + '-' + count + '-'));
        input.attr('id', input.attr('id').replace(
          input_id_re, 'id_' + prefix + '-' + count + '-'));
      });
    }

    function reenumerate_forms($forms, prefix) {
      var count = 0;
      $forms.each(function () {
        renumber_form($(this), prefix, count);
        count += 1;
      });
      $('#id_' + prefix + '-TOTAL_FORMS').val(count);
      return count;
    }

    function add_delete_link($nav_item) {
      var $form = $content.find($nav_item.find('a').attr('href'));
      $nav_item.prepend('<span class="btn-small pull-right delete-icon"><i class="fa fa-times"></i></span>');
      $nav_item.find('span.delete-icon:first').click(function () {
          var count;
          $form.remove();
          $nav_item.remove();
          count = reenumerate_forms($content.find('.tab-pane'), prefix);
          if (count === 0) { add_node(); }
      });
    }

    function add_node() {
      var $new_form = $(empty_form_html);
      var count, id, $new_nav;
      $content.append($new_form);
      $new_form = $content.find('.tab-pane:last');
      count = reenumerate_forms($content.find('.tab-pane'), prefix);
      id = 'tab-' + prefix + '-' + count;
      $new_form.attr('id', id);
      $nav.append('<li><a href="#' + id + '" data-toggle="tab">Undefined node</a></li>');
      $new_nav = $nav.find('li > a:last');
      add_delete_link($new_nav.parent());
      $new_nav.click(function () {
        $(this).tab('show');
        $('select.switchable').trigger('change');
      });
      $new_nav.tab('show');
      $('select.switchable').trigger('change');
      horizon.forms.add_password_fields_reveal_buttons($new_form);
    }

    // Connect all signals.
    $('a.add-node-link').click(add_node);
    $nav.find('li').each(function () {
      add_delete_link($(this));
    });
    $nav.find('li a').click(function () {
      window.setTimeout(function () {
        $('select.switchable').trigger('change');
      }, 0);
    });

    // Activate the first field that has errors.
    $content.find('.control-group.error').each(function () {
      if (!activated) {
        $nav.find('a[href="#' + $(this).closest('.tab-pane').attr('id') + '"]').tab('show');
        activated = true;
      }
    });

  };

  return module;
} ());
