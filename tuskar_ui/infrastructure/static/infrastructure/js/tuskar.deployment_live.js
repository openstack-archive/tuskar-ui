tuskar.deployment_live = (function () {
     'use strict';

    var module = {};

    module.init = function () {
        $("#overcloudrc").on("hide.bs.collapse", function(){
            $("span.overcloudrc").html('Show <i class="fa fa-angle-down"></i>');
        });
        $("#overcloudrc").on("show.bs.collapse", function(){
            $("span.overcloudrc").html('Hide <i class="fa fa-angle-up"></i>');
        });
    };

    horizon.addInitFunction(module.init);
    return module;
} ());
