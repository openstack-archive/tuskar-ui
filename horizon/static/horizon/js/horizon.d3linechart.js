/*
    Draw line chart in d3.

    It support 2 types of usage:
      * as a standard line chart
      * as a line chart in a modal window

    To use as a standard line chart the following data attributes need to be
    provided for a div:
      data-chart-type - must be "line_chart"
      data-url        - (string) url for the json data for the chart
      data-series     - (string) the list of series separated by comma

    Example:
      <div data-chart-type="line_chart"
           data-url="/data_url"
           data-series="cpu,ram,storage,network">
      </div>

    To use as a line chart in a modal windows the following data attributes
    need to be provided for a link:
      data-chart-type - must be "modal_line_chart"
      data-url        - (string) url for the json data for the chart
      data-series     - (string) the list of series separated by comma

    Example:
      <a data-chart-type="modal_line_chart"
         data-url="/data_url"
         data-series="network">
        Click me!
      </a>
*/

horizon.d3_line_chart = {

  init: function() {
    var self = this;

    self.init_line_charts();
    self.init_modal_chart_links();
  },

  init_line_charts: function() {
    var self = this;

    line_charts = $("div[data-chart-type='line_chart']");
    $.each(line_charts, function(index, line_chart) {
      if($(line_chart).data('modal') != true) {
        var template = horizon.templates.compiled_templates["#modal_chart_template"];
        self.init_svg(line_chart);
        self.draw(self.data(line_chart));
      }
    });
  },

  init_modal_chart_links: function() {
    var self = this;

    $(document).on('click', "a[data-chart-type='modal_line_chart']", function(event) {
      event.preventDefault();

      var template = horizon.templates.compiled_templates["#modal_chart_template"];
      $('#modal_wrapper').append(template.render({classes: "modal"}));

      var modal = $('.modal:last');
      modal.modal();

      $(modal).on('click', 'ul#interval_selector li a', function(event){
        event.preventDefault();

        self.url_options.interval = $(event.target).data('interval');
        self.draw(self.url_options);
        $("ul#interval_selector li").removeClass("active");
        $(event.target).parent().addClass("active");
      })

      self.init_svg("#modal_chart");
      self.url_options = self.data($(event.target))
      self.draw(self.url_options)
    });
  },

  init_svg: function(chart_div) {
    var self = this;

    self.margin = {top: 20, right: 80, bottom: 30, left: 50};
    self.width = 550 - self.margin.left - self.margin.right;
    self.height = 300 - self.margin.top - self.margin.bottom;

    self.svg = d3.select(chart_div)
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

  draw: function(url_options) {
    var self = this;
    var url_options = url_options || {};
    url_options.interval = url_options.interval || "1w";

    d3.json(self.json_url(url_options), function(error, data) {
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

      var legend = usage.append('g')
                        .attr('class', 'legend');

      legend.append('rect')
            .attr('x', self.width - 60)
            .attr('y', function(d, i){ return (i *  20) + 30 ;})
            .attr('width', 10)
            .attr('height', 10)
            .style('fill', function(d) { return self.color(d.name); });

      legend.append('text')
          .attr('x', self.width - 40)
          .attr('y', function(d, i){ return (i *  20) + 39;})
          .text(function(d){ return d.name.replace(/_/g, " "); });

      usages.exit().remove();
    });
  },

  data: function(element) {
    return {
      url: $(element).data("url"),
      series: $(element).data("series")
    };
  },

  json_url: function(url_options) {
    var options = $.extend({}, url_options);
    var url = options.url
    delete options.url
    return url + '?' + $.param(options);
  },

  key: function(data){
    return data.name + data.values.length + data.values[0].date + data.values[data.values.length-1].date
  },

};

horizon.addInitFunction(function () {
  horizon.d3_line_chart.init();
});
