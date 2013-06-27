/*
    Draw a non-modal line chart in d3.

    Example:
        <div id="some_sort_of_data_chart"
             class="line_chart"
             data-line-url="/url/to/get/data/from"
        </div>
*/

horizon.d3_line_chart = {
  line_charts: [],

  init: function() {
    this.line_charts = $('div[data-line-url]');

    this._initialCreation(this.line_charts);
  },

  draw: function(element, url) {
    var self = this;

    var margin = {top: 20, right: 80, bottom: 30, left: 50};
    var width = 1000 - margin.left - margin.right;
    var height = 400 - margin.top - margin.bottom;

    var svg = d3.select("#"+element)
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

  // Draw the initial d3 bars
  _initialCreation: function(charts) {
    var scope = this;
    $(charts).each(function(index, element) {
      var chart_element = $(element);

      var chart_url = chart_element.attr('data-line-url');

      scope.draw($(element).attr('id'), chart_url);
    });
  }
};
