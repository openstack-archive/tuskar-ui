tuskar.number_picker = (function () {
    'use strict';

    var module = {};

    module.init = function () {
        $('input.number-picker').removeClass(
        'form-control').wrap(
        '<div class="number_picker unselectable form-control">').before(
        '<a class="arrow-left" href="#">' +
        '<i class="fa fa-chevron-left"></i></a>').after(
        '<a class="arrow-right" href="#">' +
        '<i class="fa fa-chevron-right"></i></a>').each(
        function () {
            var $this = $(this);
            var $right_arrow = $this.next('a.arrow-right');
            var $left_arrow = $this.prev('a.arrow-left');
            if ($this.attr('readonly')) {
                $this.parent().addClass('readonly');
            }
            function change(step) {
                var value = +$this.val();
                var maximum = +$this.attr('max');
                var minimum = +$this.attr('min');
                value += step;
                if (!isNaN(maximum)) { value = Math.min(maximum, value); }
                if (!isNaN(minimum)) { value = Math.max(minimum, value); }
                $right_arrow.toggleClass('disabled', (value === maximum));
                $left_arrow.toggleClass('disabled', (value === minimum));
                $this.val(value);
                $this.trigger('change');
            }
            $right_arrow.click(function () {
                var step = +($this.attr('step') || 1);
                change(step);
            });
            $left_arrow.click(function () {
                var step = -($this.attr('step') || 1);
                change(step);
            });
            change(0);
            var step = +($this.attr('step') || 1);
            if (step !== 1) {
              $this.after('<span class="step">+' + step + '</span>');
            }
        });
    };

    horizon.addInitFunction(module.init);
    return module;
} ());
