/* global $ horizon tuskar */
tuskar.numberPicker = (function () {
    "use strict";

    var module = {};

    module.init = function () {
        $("input.number-picker").removeClass(
        "form-control").wrap(
        "<div class=\"number_picker unselectable form-control\">").before(
        "<a class=\"arrow-left\" href=\"#\">" +
        "<i class=\"fa fa-chevron-left\"></i></a>").after(
        "<a class=\"arrow-right\" href=\"#\">" +
        "<i class=\"fa fa-chevron-right\"></i></a>").each(
        function () {
            var $this = $(this);
            var $rightArrow = $this.next("a.arrow-right");
            var $leftArrow = $this.prev("a.arrow-left");
            if ($this.attr("readonly")) {
                $this.parent().addClass("readonly");
            }
            function change(step) {
                var value = +$this.val();
                var maximum = +$this.attr("max");
                var minimum = +$this.attr("min");
                value += step;
                if (!isNaN(maximum)) { value = Math.min(maximum, value); }
                if (!isNaN(minimum)) { value = Math.max(minimum, value); }
                $rightArrow.toggleClass("disabled", (value === maximum));
                $leftArrow.toggleClass("disabled", (value === minimum));
                $this.val(value);
                $this.trigger("change");
            }
            $rightArrow.click(function () {
                var rstep = +($this.attr("step") || 1);
                change(rstep);
            });
            $leftArrow.click(function () {
                var lstep = -($this.attr("step") || 1);
                change(lstep);
            });
            change(0);
            var step = +($this.attr("step") || 1);
            if (step !== 1) {
              $this.after("<span class=\"step\">+" + step + "</span>");
            }
        });
    };

    horizon.addInitFunction(module.init);
    return module;
}());
