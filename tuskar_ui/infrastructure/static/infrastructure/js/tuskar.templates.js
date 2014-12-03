/* global $ horizon tuskar Hogan */

/* Namespace for core functionality related to client-side templating. */
tuskar.templates = {
  templateIds: ["#modal_chart_template"]
};

/* Pre-loads and compiles the client-side templates. */
tuskar.templates.compileTemplates = function () {
  "use strict";

  $.each(tuskar.templates.templateIds, function (ind, templateId) {
    horizon.templates.compiled_templates[templateId] = Hogan.compile($(templateId).html());
  });
};

horizon.addInitFunction(function () {
  "use strict";

  // Load client-side template fragments and compile them.
  tuskar.templates.compileTemplates();
});
