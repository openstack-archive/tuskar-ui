tuskar.number_picker = (function () {
    'use strict';

    var module = {};

    module.init = function () {
        $('input.number-picker').removeClass(
        'form-control').attr(
        'type', 'text').wrap(
        '<div class="number_picker unselectable form-control">').before(
        '<a class="arrow-left" href="#">' +
        '<i class="fa fa-chevron-left"></i></a>').after(
        '<a class="arrow-right" href="#">' +
        '<i class="fa fa-chevron-right"></i></a>').each(
        function () {
            var $this = $(this);
            if ($this.attr('readonly')) {
                $this.parent().addClass('readonly');
            }
            $this.next('a.arrow-right').click(function () {
                $this.val((+$this.val()) + 1);
            });
            $this.prev('a.arrow-left').click(function () {
                $this.val(Math.max(0, (+$this.val()) - 1));
            });
        });
    };

    horizon.addInitFunction(module.init);
    return module;
} ());
