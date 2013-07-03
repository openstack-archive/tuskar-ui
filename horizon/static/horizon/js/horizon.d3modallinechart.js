/*
    Draw line chart in d3.

    To use, a link is required with the class .modal_chart

    Example:
        <a class="modal_chart">Click me!</a>
*/

horizon.d3_modal_line_chart = {

  init: function() {
    var self = this;

    $(document).on('click', '.modal_chart', function (evt) {
      evt.preventDefault();
      var $this = $(this);

      var template = horizon.templates.compiled_templates["#modal_chart_template"];
      $('#modal_wrapper').append(template.render());

      var modal = $('.modal:last');
      modal.modal();

      $(modal).on('click', 'ul#interval_selector li a', function(event){
        event.preventDefault();

        interval = $(event.target).data("interval");
        self.draw('/infrastructure/resource_management/racks/usage_data', {interval: interval});

        $("ul#interval_selector li").removeClass("active");
        $(event.target).parent().addClass("active");
      })

      self.init_svg();
      self.draw('/infrastructure/resource_management/racks/usage_data')
    });
  },

  init_svg: function() {
    var self = this;

    self.margin = {top: 20, right: 80, bottom: 30, left: 50};
    self.width = 700 - self.margin.left - self.margin.right;
    self.height = 400 - self.margin.top - self.margin.bottom;

    self.svg = d3.select("#modal_chart")
                 .append("svg")
                 .attr("width", self.width + self.margin.left + self.margin.right)
                 .attr("height", self.height + self.margin.top + self.margin.bottom)
                 .append("g")
                 .attr("transform", "translate(" + self.margin.left + "," + self.margin.top + ")");

    self.x = d3.time.scale().range([0, self.width]);
    self.y = d3.scale.linear().range([self.height, 0]);

    self.xAxis = d3.svg.axis()
                       .scale(self.x)
                       .orient("bottom").ticks(6);
    self.yAxis = d3.svg.axis()
                       .scale(self.y)
                       .orient("left");

    self.parse_date = d3.time.format("%Y-%m-%dT%H:%M:%S.%L").parse;

    self.line = d3.svg.line().interpolate("linear")
                             .x(function(d) { return self.x(d.date); })
                             .y(function(d) { return self.y(d.value); });

    self.color = d3.scale.category10();
  },

  draw: function(url, url_options) {
    var self = this;
    var url_options = url_options || {};
    url_options.interval = url_options.interval || "1w";

    d3.json(self.data_url(url, url_options), function(error, data) {
      data.forEach(function(d) { d.date = self.parse_date(d.date); });

      self.color.domain(d3.keys(data[0]).filter(function(key) { return key !== 'date'; }));

      var usage_values = self.color.domain().map(function(name) {
        return {
          name: name,
          values: data.map(function(d) {
            return {date: d.date, value: d[name]};
          })
        };
      });

      self.svg.selectAll(".axis").remove();
      self.x.domain(d3.extent(data, function(d) { return d.date; }));
      self.y.domain([0, 15]);

      self.svg.append("g")
              .attr("transform", "translate(0," + self.height + ")")
              .attr("class", "axis")
              .call(self.xAxis);
      self.svg.append("g")
              .attr("class", "axis")
              .call(self.yAxis)

      var usages = self.svg.selectAll(".usage")
                           .data(usage_values, function(d) { return self.key(d) });

      var usage = usages.enter().append("g")
                                .attr("class", "usage");

      usage.append("path")
           .attr("d", function(d) { return self.line(d.values); })
           .style("stroke", function(d) { return self.color(d.name); })
           .style("fill", "none")
           .style("stroke-width", 3);

      usages.exit().remove();
    });
  },

  data_url: function(url, options) {
    return url + '?' + $.param(options);
  },

  key: function(data){
    return data.name + data.values.length + data.values[0].date + data.values[data.values.length-1].date
  },

};

horizon.addInitFunction(function () {
  horizon.d3_modal_line_chart.init();
});
