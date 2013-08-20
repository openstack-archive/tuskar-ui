/* Namespace for core functionality related to client-side templating. */
tuskar.templates = {
  template_ids: ["#modal_chart_template"],
};

/* Pre-loads and compiles the client-side templates. */
tuskar.templates.compile_templates = function () {
  $.each(tuskar.templates.template_ids, function (ind, template_id) {
    horizon.templates.compiled_templates[template_id] = Hogan.compile($(template_id).html());
  });
};

horizon.addInitFunction(function () {
  // Load client-side template fragments and compile them.
  tuskar.templates.compile_templates();
});
