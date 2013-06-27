/*
    Draw line chart in d3.

    To use, a link is required with the class .modal_chart

    Example:
        <a class="modal_chart">Click me!</a>
*/

horizon.d3_modal_line_chart = {

  init: function() {
    var self = this;

    // Load modals for modal chart links
    $(document).on('click', '.modal_chart', function (evt) {
      evt.preventDefault();
      var $this = $(this);

      var template = horizon.templates.compiled_templates["#modal_chart_template"];
      $('#modal_wrapper').append(template.render());

      var modal = $('.modal:last');
      modal.modal();

      self.draw('/infrastructure/resource_management/racks/usage_data')
    });
  },

  draw: function(url) {
    var self = this;

    var margin = {top: 20, right: 80, bottom: 30, left: 50};
    var width = 700 - margin.left - margin.right;
    var height = 400 - margin.top - margin.bottom;

    var svg = d3.select("#modal_chart")
                .append("svg")
                .attr("width", width + margin.left + margin.right)
                .attr("height", height + margin.top + margin.bottom)
                .append("g")
                .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    var x = d3.time.scale().range([0, width]);
    var y = d3.scale.linear().range([height, 0]);

    var xAxis = d3.svg.axis()
                      .scale(x)
                      .orient("bottom");
    var yAxis = d3.svg.axis()
                  .scale(y)
                  .orient("left");

    var parseDate = d3.time.format("%Y-%m-%dT%H:%M:%S.%L").parse;

    var line = d3.svg.line().interpolate("linear")
                            .x(function(d) { return x(d.date); })
                            .y(function(d) { return y(d.value); });

    var color = d3.scale.category10();

    d3.json(url, function(error, data) {
      data.forEach(function(d) {
        d.date = parseDate(d.date);
      });

      color.domain(d3.keys(data[0]).filter(function(key) { return key !== 'date'; }));

      var usage_values = color.domain().map(function(name) {
        return {
          name: name,
          values: data.map(function(d) {
            return {date: d.date, value: d[name]};
          })
        };
      });

      x.domain(d3.extent(data, function(d) { return d.date; }));
      y.domain([
        d3.min(usage_values, function(u) { return d3.min(u.values, function(v) { return v.value; }) - 1; }),
        d3.max(usage_values, function(u) { return d3.max(u.values, function(v) { return v.value; }) + 6; })
      ]);

      svg.append("g")
         .attr("transform", "translate(0," + height + ")")
         .attr("class", "axis")
         .call(xAxis);
      svg.append("g")
         .attr("class", "axis")
         .call(yAxis)

      var usage = svg.selectAll(".usage")
                    .data(usage_values)
                    .enter().append("g");

      usage.append("path")
        .attr("d", function(d) { return line(d.values); })
        .style("stroke", function(d) { return color(d.name); })
        .style("fill", "none")
        .style("stroke-width", 3);
    });
  },

};

horizon.addInitFunction(function () {
  horizon.d3_modal_line_chart.init();
});
