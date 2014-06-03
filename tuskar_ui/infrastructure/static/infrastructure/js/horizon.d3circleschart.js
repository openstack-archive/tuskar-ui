/*
    Draw circles chart in d3.

    To use, a div is required with the data attributes
    data-chart-type="circles_chart", data-url and data-size in the
    div.

    data-chart-type - must be "circles_chart" so chart gets initialized
    data-url        - (string) url for the json data for the chart
    data-time       - (string) time parameter, gets appended to url as time=...
    data-size       - (integer) size of the circles in pixels

    If used in popup, initialization must be made manually e.g.:
      addHorizonLoadEvent(function() {
          horizon.d3_circles_chart.init('.html_element');
          horizon.d3_circles_chart.init('.health_chart');
      });


    Example:
      <div class="html_element"
           data-chart-type="circles_chart"
           data-url="/infrastructure/racks/1/top_communicating.json?cond=to"
           data-time="now"
           data-size="22">
      </div>

    There are control elements for the cirles chart, implementing some commands
    that will be executed over the chart.

    1. The selectbox for time change, implements ChangeTime command. It has to
    have data attribute data-circles-chart-command="change_time", with defined
    receiver as jquery selector (selector can point to more elements and it will
    execute the command on all of them) e.g. data-receiver="#rack_health_chart"
    Option value is then appended to url and chart is refreshed.

    Example
    <div class="span3 circles_chart_time_picker">
      <select data-circles-chart-command="change_time"
              data-receiver="#rack_health_chart">
        <option value="now">Now</option>
        <option value="yesterday">Yesterday</option>
        <option value="last_week">Last Week</option>
        <option value="last_month">Last Month</option>
      </select>
    </div>
    <div class="clear"></div>

    2. Bootstrap tabs for switching different circle_charts implement command
    ChangeUrl. It has to have data attribute data-circles-chart-command="change_url",
    with defined receiver as jquery selector (selector can point to more elements and
    it will execute the command on all of them) e.g. data-receiver="#rack_health_chart"

    Inner li a element has to have  attribute data-url, e.g.
    data-url="/infrastructure/racks/1/top_communicating.json?type=alerts"

    The url of the chart is then switched and chart is refreshed.

    <ul class="nav nav-tabs"
        data-circles-chart-command="change_url"
        data-receiver="#rack_health_chart">
      <li class="active">
        <a data-url="/infrastructure/racks/1/top_communicating.json?type=overall_health" href="#">
          Overall Health</a>
      </li>
      <li>
        <a data-url="/infrastructure/racks/1/top_communicating.json?type=alerts" href="#">
          Alerts</a>
      </li>
      <li>
        <a data-url="/infrastructure/racks/1/top_communicating.json?type=capacities" href="#">
          Capacities</a>
      </li>
      <li>
        <a data-url="/infrastructure/racks/1/top_communicating.json?type=status" href="#">
          Status</a>
      </li>
    </ul>
*/


horizon.d3_circles_chart = {
  CirclesChart: function(chart_class, html_element){
    this.chart_class = chart_class;
    this.html_element = html_element;

    var jquery_element = $(html_element);
    this.size = jquery_element.data('size');
    this.time = jquery_element.data('time');
    this.url = jquery_element.data('url');

    this.final_url = this.url;
    if (this.final_url.indexOf('?') > -1){
      this.final_url += '&time=' + this.time;
    }else{
      this.final_url += '?time=' + this.time;
    }

    this.time = jquery_element.data('time');
    this.data = [];

    this.refresh = refresh;
    function refresh(){
      var self = this;
      this.jqxhr = $.getJSON( this.final_url, function() {
            //FIXME add loader in the target element
          })
          .done(function(data) {
            // FIXME find a way how to only update graph with new data
            // not delete and create
            $(self.html_element).html("");

            self.data = data.data;
            self.settings = data.settings;
            self.chart_class.render(self.html_element, self.size, self.data, self.settings);
          })
          .fail(function() {
            // FIXME add proper fail message
            console.log( "error" ); })
          .always(function() {
            // FIXME add behaviour that should be always done
          });
    }
  },
  init: function(selector, settings) {
    var self = this;
    $(selector).each(function() {
      self.refresh(this);
    });
    self.bind_commands();
  },
  refresh: function(html_element){
    var chart = new this.CirclesChart(this, html_element);
    // FIXME save chart objects somewhere so I can use them again when
    // e.g. I am swithing tabs, or if I want to update them
    // via web sockets
    // this.charts.add_or_update(chart)
    chart.refresh();
  },
  render: function(html_element, size, data, settings){
    var self = this;
    // FIXME rewrite to scatter plot once we have some cool D3 chart
    // library
    var width = size + 4,
        height = size + 4,
        round = size / 2,
        center_x = width / 2,
        center_y = height / 2;

    var svg = d3.select(html_element).selectAll("svg")
      .data(data)
      .enter().append("svg")
      .attr("width", width)
      .attr("height", height);

    // FIXME use some pretty tooltip from some library we will use
    // this one is just temporary
    var tooltip = d3.select(html_element).append("div")
      .style("position", "absolute")
      .style("z-index", "10")
      .style("visibility", "hidden")
      .style("min-width", "100px")
      .style("max-width", "110px")
      .style("min-height", "30px")
      .style("border", "1px ridge grey")
      .style("background-color", "white")
      .text(function(d) { "a simple tooltip"; });

    var circle = svg.append("circle")
        .attr("r", round)//function(d) { return d.r; })// can be sent form server
        .attr("cx", center_x)
        .attr("cy", center_y)
        .attr("stroke", "#cecece")
        .attr("stroke-width", function (d) {
          return 1;
        })
        .style("fill", function (d) {
          if (d.color) {
            return d.color;
          } else if (settings.scale == "linear_color_scale") {
            return self.linear_color_scale(d.percentage, settings.domain, settings.range);
          }
        })
        .on("mouseover", function (d) {
          if (d.tooltip) {
            tooltip.html(d.tooltip);
          } else {
            tooltip.html(d.name + "<br/>" + d.status);
          }
          tooltip.style("visibility", "visible");
        })
        .on("mousemove", function (d) {
            tooltip.style("top", (event.pageY-10)+"px").style("left",(event.pageX+10)+"px");
        })
        .on("mouseout", function (d) {
            tooltip.style("visibility", "hidden");
        });

    /*
    // or just d3 title element
    circle.append("svg:title")
      .text(function(d) { return d.x; });

    */
  },
  linear_color_scale: function(percentage, domain, range){
    usage_color = d3.scale.linear()
      .domain(domain)
      .range(range);
    return usage_color(percentage);
  },
  bind_commands: function (){
    var change_time_command_selector = 'select[data-circles-chart-command="change_time"]';
    var change_url_command_selector = '[data-circles-chart-command="change_url"]';
    var self = this;
    bind_change_time = function () {
      $(change_time_command_selector).each(function() {
        $(this).change(function () {
          var invoker = $(this);
          var command = new self.Command.ChangeTime(self, invoker);
          command.execute();
        });
      });
    };
    bind_change_url = function(){
      $(change_url_command_selector + ' a').click(function (e) {
        // Bootstrap tabs functionality
        e.preventDefault();
        $(this).tab('show');

        // Command for url change and refresh
        var invoker = $(this);
        var command = new self.Command.ChangeUrl(self, invoker);
        command.execute();
      });
    };
    bind_change_time();
    bind_change_url();
  },
  Command: {
    ChangeTime: function (chart_class, invoker){
      // Invoker of the command should know about it's receiver.
      // Also invoker brings all parameters of the command.
      this.receiver_selector = invoker.data('receiver');
      this.new_time = invoker.find("option:selected").val();

      this.execute = execute;
      function execute(){
          var self = this;
          $(this.receiver_selector).each(function(){
            // change time of the chart
            $(this).data('time', self.new_time);
            // refresh the chart
            chart_class.refresh(this);
          });
      }
    },
    ChangeUrl: function (chart_class, invoker, new_url){
      // Invoker of the command should know about it's receiver.
      // Also invoker brings all parameters of the command.
      this.receiver_selector = invoker.parents('ul').first().data('receiver');
      this.new_url = invoker.data('url');

      this.execute = execute;
      function execute(){
        var self = this;
        $(this.receiver_selector).each(function(){
          // change time of the chart
          $(this).data('url', self.new_url);
          // refresh the chart
          chart_class.refresh(this);
        });
      }
    }
  }
};

/* init the graphs */
horizon.addInitFunction(function () {
    horizon.d3_circles_chart.init('div[data-chart-type="circles_chart"]');
});

