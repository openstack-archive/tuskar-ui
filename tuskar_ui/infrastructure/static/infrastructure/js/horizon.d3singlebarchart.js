/*
  Used for animating and displaying single-bar information using
  D3js rect.

  Usage:
    In order to have single bars that work with this, you need to have a
    DOM structure like this in your Django template:

    Example:
    <div class="flavor_usage_bar"
      data-popup-free='<p>Capacity remaining by flavors: </p>
        {{resource_class.all_instances_flavors_info}}'
      data-single-bar-orientation="horizontal"
      data-single-bar-height="50"
      data-single-bar-width="100%"
      data-single-bar-used="{{ resource_class.all_used_instances_info }}"
      data-single-bar-auto-scale-selector=".flavors_scale_selector"
      data-single-bar-color-scale-range='["#000060", "#99FFFF"]'>
    </div>

    The available data- attributes are:
      data-popup-free, data-popup-used, data-popup-average OPTIONAL
          Html content of popups that will be displayed over this areas.

      data-single-bar-orientation REQUIRED
          String representing orientation of the bar.Can be "horizontal"
          or "vertical"

      data-single-bar-height REQUIRED
          Integer or string with percent mark format e.g. "50%". Determines
          the total height of the bar.

      data-single-bar-width="100%" REQUIRED
          Integer or string with percent mark format e.g. "50%". Determines
          the total width of the bar.

      data-single-bar-used="integer" REQUIRED
          1. Integer
            Integer representing the percent used.
          2. Array
            Array of following structure:
            [{"popup_used": "Popup html 1", "used_instances": "5"},
             {"popup_used": "Popup html 2", "used_instances": "15"},....]

            used_instances: Integer representing the percent used.
            popup_used: Html that will be displayed in popup window over
              this area.

      data-single-bar-used-average="integer" OPTIONAL
          Integer representing the average usage in percent of given
          single-bar.

      data-single-bar-auto-scale-selector OPTIONAL
          Jquery selector of bar elements that have Integer
          data-single-bar-used attribute. It then takes maximum of these
          values as 100% of the liner scale of the colors.
          So the array representing linear scale interval is set
          automatically.This then maps to data-single-bar-color-scale-range.
          (arrays must have the same structure)

      single-bar-color-scale-range OPTIONAL
          Array representing linear scale interval that is set manually.
          E.g "[0,10]". This then maps to data-single-bar-color-scale-range.
          (arrays must have the same structure)

      data-single-bar-color-scale-range OPTIONAL
          Array representing linear scale of colors.
          E.g '["#000060", "#99FFFF"]'

*/

horizon.d3_single_bar_chart = {
  SingleBarChart: function(chart_class, html_element){
    var self = this;
    self.chart_class = chart_class;

    self.html_element = html_element;
    self.jquery_element = $(self.html_element);
    // Using only percent, so limit is 100%
    self.single_bar_limit = 100;

    self.single_bar_used = $.parseJSON(self.jquery_element.attr('data-single-bar-used'));
    self.average_used = parseInt(self.jquery_element.attr('data-single-bar-average-used'), 10);

    self.data = {};

    // Percentage and used_px  count
    if ($.isArray(self.single_bar_used)){
      self.data.used_px = 0;
      self.data.percentage_used = Array();
      self.data.tooltip_used_contents = Array();
      for (var i = 0; i < self.single_bar_used.length; ++i) {
        if (!isNaN(self.single_bar_limit) && !isNaN(self.single_bar_used[i].used_instances)) {
          used = Math.round((self.single_bar_used[i].used_instances / self.single_bar_limit) * 100);

          self.data.percentage_used.push(used);
          // for multi-bar chart, tooltip is in the data
          self.data.tooltip_used_contents.push(self.single_bar_used[i].popup_used);

          self.data.used_px += self.jquery_element.width() / 100 * used;
        } else { // If NaN self.data.percentage_used is 0

        }
      }

    }
    else {
      if (!isNaN(self.single_bar_limit) && !isNaN(self.single_bar_used)) {
        self.data.percentage_used = Math.round((self.single_bar_used / self.single_bar_limit) * 100);
        self.data.used_px = self.jquery_element.width() / 100 * self.data.percentage_used;

      } else { // If NaN self.data.percentage_used is 0
        self.data.percentage_used = 0;
        self.data.used_px = 0;
      }

      if (!isNaN(self.single_bar_limit) && !isNaN(self.average_used)) {
        self.data.percentage_average = ((self.average_used / self.single_bar_limit) * 100);
      } else {
        self.data.percentage_average = 0;
      }
    }

    // Width and height of bar
    self.data.width = self.jquery_element.data('single-bar-width');
    self.data.height = self.jquery_element.data('single-bar-height');

    // Color scales
    self.auto_scale_selector = function () {
      return self.jquery_element.data('single-bar-auto-scale-selector');
    };
    self.is_auto_scaling = function () {
      return self.auto_scale_selector();
    };
    self.auto_scale = function () {
      var max_scale = 0;
      $(self.auto_scale_selector()).each(function() {
        var scale = parseInt($(this).data('single-bar-used'), 10);
        if (scale > max_scale)
          max_scale = scale;
      });
      return [0, max_scale];
    };

    if (self.jquery_element.data('single-bar-color-scale-domain'))
      self.data.color_scale_domain =
        self.jquery_element.data('single-bar-color-scale-domain');
    else if (self.is_auto_scaling())
      // Dynamically set scale based on biggest value
      self.data.color_scale_domain = self.auto_scale();
    else
      self.data.color_scale_domain = [0,100];

    if (self.jquery_element.data('single-bar-color-scale-range'))
      self.data.color_scale_range =
        self.jquery_element.data('single-bar-color-scale-range');
    else
      self.data.color_scale_range = ["#000000", "#0000FF"];

    // Tooltips data
    self.data.popup_average = self.jquery_element.data('popup-average');
    self.data.popup_free = self.jquery_element.data('popup-free');
    self.data.popup_used = self.jquery_element.data('popup-used');

    // Orientation of the Bar chart
    self.data.orientation = self.jquery_element.data('single-bar-orientation');

    // Refresh method
    self.refresh = function (){
      self.chart_class.render(self.html_element, self.data);
    };
  },
  BaseComponent: function(data){
    var self = this;

    self.data = data;

    self.w = data.width;
    self.h = data.height;
    self.lvl_curve = 3;
    self.bkgrnd = "#F2F2F2";
    self.frgrnd = "grey";
    self.color_scale_max = 25;

    self.percentage_used = data.percentage_used;
    self.total_used_perc = 0;
    self.used_px = data.used_px;
    self.percentage_average = data.percentage_average;
    self.tooltip_used_contents = data.tooltip_used_contents;

    // set scales
    self.usage_color = d3.scale.linear()
      .domain(data.color_scale_domain)
      .range(data.color_scale_range);

    // return true if it renders used percentage multiple in one chart
    self.used_multi = function (){
      return ($.isArray(self.percentage_used));
    };

    // deals with percentage if there should be multiple in one chart
    self.used_multi_iterator = 0;
    self.percentage_used_value = function(){
      if (self.used_multi()){
        return self.percentage_used[self.used_multi_iterator];
      } else {
        return self.percentage_used;
      }
    };
    // deals with html tooltips if there should be multiple in one chart
    self.tooltip_used_value = function (){
      if (self.used_multi()){
        return self.tooltip_used_contents[self.used_multi_iterator];
      } else {
        return "";
      }
    };

    // return true if it chart is oriented horizontally
    self.horizontal_orientation = function (){
      return (self.data.orientation == "horizontal");
    };

  },
  UsedComponent: function(base_component){
    var self = this;
    self.base_component = base_component;

    // FIXME would be good to abstract all attributes and resolve orientation inside
    if (base_component.horizontal_orientation()){
      // Horizontal Bars
      self.y = 0;
      self.x = base_component.total_used_perc + "%";
      self.width = 0;
      self.height = base_component.h;
      self.trasition_attr = "width";
      self.trasition_value = base_component.percentage_used_value() + "%";
    } else { // Vertical Bars
      self.y = base_component.h;
      self.x = 0;
      self.width = base_component.w;
      self.height = base_component.percentage_used_value() + "%";
      self.trasition_attr = "y";
      self.trasition_value = 100 - base_component.percentage_used_value() + "%";
    }

    self.append =  function(bar, tooltip){
      var used_component = self;
      var base_component = self.base_component;

      bar.append("rect")
        .attr("class", "usedbar")
        .attr("y", used_component.y)
        .attr("x", used_component.x)
        .attr("width", used_component.width)
        .attr("height", used_component.height)
        //.attr("rx", base_component.lvl_curve)
        //.attr("ry", base_component.lvl_curve)
        .style("fill", base_component.usage_color(base_component.percentage_used_value()))
        .style("stroke", "#bebebe")
        .style("stroke-width", 0)
        .attr("d", base_component.percentage_used_value())
        .attr("popup-used", base_component.tooltip_used_value())
        .on("mouseover", function(d){
          if ($(this).attr('popup-used')){
            tooltip.html($(this).attr('popup-used'));
          }
          tooltip.style("visibility", "visible");})
        .on("mousemove", function(d){tooltip.style("top",
          (event.pageY-10)+"px").style("left",(event.pageX+10)+"px");})
        .on("mouseout", function(d){tooltip.style("visibility", "hidden");})
        .transition()
          .duration(500)
          .attr(used_component.trasition_attr, used_component.trasition_value);
    };
  },
  AverageComponent: function(base_component){
    var self = this;
    self.base_component = base_component;

    // FIXME would be good to abstract all attributes and resolve orientation inside
    if (base_component.horizontal_orientation()){
      // Horizontal Bars
      self.y = 1;
      self.x = 0;
      self.width = 1;
      self.height = base_component.h;
      self.trasition_attr = "x";
      self.trasition_value = base_component.percentage_average + "%";
    } else { // Vertical Bars
      self.y = 0;
      self.x = 0;
      self.width = base_component.w;
      self.height = 1;
      self.trasition_attr = "y";
      self.trasition_value = 100 - base_component.percentage_average + "%";
    }

    self.append = function(bar, tooltip){
      var average_component = self;
      var base_component = self.base_component;

      bar.append("rect")
        .attr("y", average_component.y)
        .attr("x", average_component.x)
        .attr("class", "average")
        .attr("height", average_component.height)
        .attr("width", average_component.width)
        .style("fill", "black")
        .on("mouseover", function(){tooltip.style("visibility", "visible");})
        .on("mousemove", function(){tooltip.style("top",
          (event.pageY-10)+"px").style("left",(event.pageX+10)+"px");})
        .on("mouseout", function(){tooltip.style("visibility", "hidden");})
        .transition()
          .duration(500)
          .attr(average_component.trasition_attr, average_component.trasition_value);
    };
  },
  /* TODO rewrite below as components */
  /* FIXME use some pretty tooltip from some library we will use
   * this one is just temporary */
  append_tooltip: function(tooltip, html_content){
    return tooltip
      .style("position", "absolute")
      .style("z-index", "10")
      .style("visibility", "hidden")
      .style("min-width", "100px")
      .style("max-width", "200px")
      .style("min-height", "30px")
      .style("max-height", "150px")
      .style("border", "1px ridge grey")
      .style("padding", "8px")
      .style("padding-top", "5px")
      .style("background-color", "white")
      .html(html_content);
  },
  append_unused: function(bar, base_component, tooltip_free){
    bar.append("rect")
      .attr("y", 0)
      .attr("width", base_component.w)
      .attr("height", base_component.h)
      .attr("rx", base_component.lvl_curve)
      .attr("ry", base_component.lvl_curve)
      .style("fill", base_component.bkgrnd)
      .style("stroke", "#e0e0e0")
      .style("stroke-width", 1)
      .on("mouseover", function(d){tooltip_free.style("visibility", "visible");})
      .on("mousemove", function(d){tooltip_free.style("top",
        (event.pageY-10)+"px").style("left",(event.pageX+10)+"px");})
      .on("mouseout", function(d){tooltip_free.style("visibility", "hidden");});
  },
  // TODO This have to be enhanced, so this library can replace jtomasek capacity charts
  append_text: function(bar, base_component, tooltip){
    bar.append("text")
      .text("FREE")
      .attr("y", base_component.h/2)
      .attr("x", 3)
      .attr("dominant-baseline", "middle")
      .attr("font-size", 13)
      .on("mouseover", function(d){tooltip.style("visibility", "visible");})
      .on("mousemove", function(d){tooltip.style("top",
        (event.pageY-10)+"px").style("left",(event.pageX+10)+"px");})
      .on("mouseout", function(d){tooltip.style("visibility", "hidden");})
      .transition()
        .duration(500)
        .attr("x", function() {
          // FIXME when another panel is active, this page is hidden and used_px return 0
          // text is then badly positioned, quick fix will be to refresh charts when panel
          // is switched. Need to find better solution.
          if (base_component.total_used_perc > 90 && base_component.used_px > 25)
            return base_component.used_px - 20;
          else
            return base_component.used_px + 20;
        });
  },
  append_border: function(bar){
    bar.append("rect")
      .attr("x", 0)
      .attr("y", 0)
      .attr("height", '100%')
      .attr("width", '100%')
      .style("stroke", "#bebebe")
      .style("fill", "none")
      .style("stroke-width", 1);
  },
  //  INIT
  init: function() {
    var self = this;
    this.single_bars = $('div[data-single-bar-used]');

    this.single_bars.each(function() {
      self.refresh(this);
    });
  },
  refresh: function(html_element){
    var chart = new this.SingleBarChart(this, html_element);
    // FIXME save chart objects somewhere so I can use them again when
    // e.g. I am swithing tabs, or if I want to update them
    // via web sockets
    // this.charts.add_or_update(chart)
    chart.refresh();
  },
  render: function(html_element, data) {
    var jquery_element  = $(html_element);

    // Initialize base_component
    var base_component = new this.BaseComponent(data);

    // Bar
    var bar_html = d3.select(html_element);

    // Tooltips
    var tooltip_average = bar_html.append("div");
    if (data.popup_average)
      tooltip_average = this.append_tooltip(tooltip_average, data.popup_average);

    var tooltip_free = bar_html.append("div");
    if (data.popup_free)
      tooltip_free = this.append_tooltip(tooltip_free, data.popup_free);

    var tooltip_used = bar_html.append("div");
    if (data.popup_used)
      tooltip_used = this.append_tooltip(tooltip_used, data.popup_used);

    // append layout for bar chart
    var bar = bar_html.append("svg:svg")
      .attr("class", "chart")
      .attr("width", base_component.w)
      .attr("height", base_component.h)
      .style("background-color", "white")
      .append("g");
    var used_component;

    // append Unused resources Bar
    this.append_unused(bar, base_component, tooltip_free);

    if (base_component.used_multi()){
      // If Used is shown as multiple values in one chart
      for (var i = 0; i < base_component.percentage_used.length; ++i) {
        // FIXME write proper iterator
        base_component.used_multi_iterator = i;

        // Use general tooltip, content of tooltip will be changed
        // by inner used compoentnts on their hover
        tooltip_used = this.append_tooltip(tooltip_used, "");

        // append used so it will be shown as multiple values in one chart
        used_component = new this.UsedComponent(base_component);
        used_component.append(bar, tooltip_used);

        // append Used resources to Bar
        base_component.total_used_perc += base_component.percentage_used_value();
      }

      // append Text to Bar
      this.append_text(bar, base_component, tooltip_free);

    } else {
      // used is show as one value it the chart
      used_component = new this.UsedComponent(base_component);
      used_component.append(bar, tooltip_used);

      // append average value to Bar
      var average_component = new this.AverageComponent(base_component);
      average_component.append(bar, tooltip_average);
    }
    // append border of whole Bar
    this.append_border(bar);
  }
};


horizon.addInitFunction(function () {
  horizon.d3_single_bar_chart.init();
});
