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
          horizon.d3CirclesChart.init(".htmlElement");
          horizon.d3CirclesChart.init(".health_chart");
      });


    Example:
      <div class="htmlElement"
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
/* global $ horizon d3 console */
/* eslint no-use-before-define: [1, "nofunc"] */

horizon.d3CirclesChart = {
  CirclesChart: function (chartClass, htmlElement) {
    "use strict";

    this.chartClass = chartClass;
    this.htmlElement = htmlElement;
    var jqueryElement = $(htmlElement);
    this.size = jqueryElement.data("size");
    this.time = jqueryElement.data("time");
    this.url = jqueryElement.data("url");
    this.finalUrl = this.url;
    if (this.finalUrl.indexOf("?") > -1) {
      this.finalUrl += "&time=" + this.time;
    } else {
      this.finalUrl += "?time=" + this.time;
    }
    this.time = jqueryElement.data("time");
    this.data = [];
    this.refresh = refresh;
    function refresh() {
      var self = this;
      this.jqxhr = $.getJSON(this.finalUrl, function () {
      }).done(function (data) {
        // FIXME find a way how to only update graph with new data
        // not delete and create
        $(self.htmlElement).html("");
        self.data = data.data;
        self.settings = data.settings;
        self.chartClass.render(self.htmlElement, self.size, self.data, self.settings);
      }).fail(function () {
        // FIXME add proper fail message
        console.log("error");
      }).always(function () {
      });
    }
  },
  init: function (selector) {
    "use strict";

    var self = this;
    $(selector).each(function () {
      self.refresh(this);
    });
    self.bindCommands();
  },
  refresh: function (htmlElement) {
    "use strict";

    var chart = new this.CirclesChart(this, htmlElement);
    // FIXME save chart objects somewhere so I can use them again when
    // e.g. I am swithing tabs, or if I want to update them
    // via web sockets
    // this.charts.add_or_update(chart)
    chart.refresh();
  },
  render: function (htmlElement, size, data, settings) {
    "use strict";

    var self = this;
    // FIXME rewrite to scatter plot once we have some cool D3 chart
    // library
    var width = size + 4, height = size + 4, round = size / 2, centerX = width / 2, centerY = height / 2;
    var svg = d3.select(htmlElement).selectAll("svg").data(data).enter().append("svg").attr("width", width).attr("height", height);
    // FIXME use some pretty tooltip from some library we will use
    // this one is just temporary
    var tooltip = d3.select(htmlElement).append("div").style("position", "absolute").style("z-index", "10").style("visibility", "hidden").style("min-width", "100px").style("max-width", "110px").style("min-height", "30px").style("border", "1px ridge grey").style("background-color", "white").text(function () {
      "a simple tooltip";
    });
    // var circle =
    svg.append("circle").attr("r", round)  //function(d) { return d.r; })// can be sent form server
.attr("cx", centerX).attr("cy", centerY).attr("stroke", "#cecece").attr("stroke-width", function () {
      return 1;
    }).style("fill", function (d) {
      if (d.color) {
        return d.color;
      } else if (settings.scale === "linearColorScale") {
        return self.linearColorScale(d.percentage, settings.domain, settings.range);
      }
    }).on("mouseover", function (event) {
      if (event.tooltip) {
        tooltip.html(event.tooltip);
      } else {
        tooltip.html(event.name + "<br/>" + event.status);
      }
      tooltip.style("visibility", "visible");
    }).on("mousemove", function (event) {
      tooltip.style("top", event.pageY - 10 + "px").style("left", event.pageX + 10 + "px");
    }).on("mouseout", function () {
      tooltip.style("visibility", "hidden");
    });  /*
    // or just d3 title element
    circle.append("svg:title")
      .text(function(d) { return d.x; });

    */
  },
  linearColorScale: function (percentage, domain, range) {
    "use strict";

    var usageColor = d3.scale.linear().domain(domain).range(range);
    return usageColor(percentage);
  },
  bindCommands: function () {
    "use strict";

    var changeTimeCommandSelector = "select[data-circles-chart-command=\"change_time\"]";
    var changeUrlCommandSelector = "[data-circles-chart-command=\"change_url\"]";
    var self = this;
    var bindChangeTime = function () {
      $(changeTimeCommandSelector).each(function () {
        $(this).change(function () {
          var invoker = $(this);
          var command = new self.Command.ChangeTime(self, invoker);
          command.execute();
        });
      });
    };
    var bindChangeUrl = function () {
      $(changeUrlCommandSelector + " a").click(function (e) {
        // Bootstrap tabs functionality
        e.preventDefault();
        $(this).tab("show");
        // Command for url change and refresh
        var invoker = $(this);
        var command = new self.Command.ChangeUrl(self, invoker);
        command.execute();
      });
    };
    bindChangeTime();
    bindChangeUrl();
  },
  Command: {
    ChangeTime: function (chartClass, invoker) {
      "use strict";

      // Invoker of the command should know about it's receiver.
      // Also invoker brings all parameters of the command.
      this.receiverSelector = invoker.data("receiver");
      this.newTime = invoker.find("option:selected").val();
      this.execute = execute;
      function execute() {
        var self = this;
        $(this.receiverSelector).each(function () {
          // change time of the chart
          $(this).data("time", self.newTime);
          // refresh the chart
          chartClass.refresh(this);
        });
      }
    },
    ChangeUrl: function (chartClass, invoker) {
      "use strict";

      // Invoker of the command should know about it's receiver.
      // Also invoker brings all parameters of the command.
      this.receiverSelector = invoker.parents("ul").first().data("receiver");
      this.newUrl = invoker.data("url");
      this.execute = execute;
      function execute() {
        var self = this;
        $(this.receiverSelector).each(function () {
          // change time of the chart
          $(this).data("url", self.newUrl);
          // refresh the chart
          chartClass.refresh(this);
        });
      }
    }
  }
};
/* init the graphs */
horizon.addInitFunction(function () {
  "use strict";

  horizon.d3CirclesChart.init("div[data-chart-type=\"circles_chart\"]");
});
