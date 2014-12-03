/*
  Used for animating and displaying single-bar information using
  D3js rect.

  Usage:
    In order to have single bars that work with this, you need to have a
    DOM structure like this in your Django template:

    Example:
    <div class="flavor_usage_bar"
      data-popup-free="<p>Capacity remaining by flavors: </p>
        {{resource_class.all_instances_flavors_info}}"
      data-single-bar-orientation="horizontal"
      data-single-bar-height="50"
      data-single-bar-width="100%"
      data-single-bar-used="{{ resource_class.all_used_instances_info }}"
      data-single-bar-auto-scale-selector=".flavors_scale_selector"
      data-single-bar-color-scale-range="[\"#000060\", \"#99FFFF\"]">
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
            [{"popupUsed": "Popup html 1", "used_instances": "5"},
             {"popupUsed": "Popup html 2", "used_instances": "15"},....]

            used_instances: Integer representing the percent used.
            popupUsed: Html that will be displayed in popup window over
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
          E.g "[\"#000060\", \"#99FFFF\"]"

*/

/* global $ horizon d3 */

horizon.d3SingleBarChart = {
  SingleBarChart: function(chartClass, htmlElement){
    "use strict";

    var self = this;
    self.chartClass = chartClass;

    self.htmlElement = htmlElement;
    self.jqueryElement = $(self.htmlElement);
    // Using only percent, so limit is 100%
    self.singleBarLimit = 100;

    self.singleBarUsed = $.parseJSON(self.jqueryElement.attr("data-single-bar-used"));
    self.averageUsed = parseInt(self.jqueryElement.attr("data-single-bar-average-used"), 10);

    self.data = {};

    // Percentage and usedpx  count
    if ($.isArray(self.singleBarUsed)){
      self.data.usedpx = 0;
      self.data.percentageUsed = [];
      self.data.tooltipUsedContents = [];
      for (var i = 0; i < self.singleBarUsed.length; ++i) {
        if (!isNaN(self.singleBarLimit) && !isNaN(self.singleBarUsed[i].used_instances)) {
          var used = Math.round((self.singleBarUsed[i].used_instances / self.singleBarLimit) * 100);

          self.data.percentageUsed.push(used);
          // for multi-bar chart, tooltip is in the data
          self.data.tooltipUsedContents.push(self.singleBarUsed[i].popupUsed);

          self.data.usedpx += self.jqueryElement.width() / 100 * used;
        }
      }

    }
    else {
      if (!isNaN(self.singleBarLimit) && !isNaN(self.singleBarUsed)) {
        self.data.percentageUsed = Math.round((self.singleBarUsed / self.singleBarLimit) * 100);
        self.data.usedpx = self.jqueryElement.width() / 100 * self.data.percentageUsed;

      } else { // If NaN self.data.percentageUsed is 0
        self.data.percentageUsed = 0;
        self.data.usedpx = 0;
      }

      if (!isNaN(self.singleBarLimit) && !isNaN(self.averageUsed)) {
        self.data.percentageAverage = ((self.averageUsed / self.singleBarLimit) * 100);
      } else {
        self.data.percentageAverage = 0;
      }
    }

    // Width and height of bar
    self.data.width = self.jqueryElement.data("single-bar-width");
    self.data.height = self.jqueryElement.data("single-bar-height");

    // Color scales
    self.autoScaleSelector = function () {
      return self.jqueryElement.data("single-bar-auto-scale-selector");
    };
    self.isAutoScaling = function () {
      return self.autoScaleSelector();
    };
    self.autoScale = function () {
      var maxScale = 0;
      $(self.autoScaleSelector()).each(function() {
        var scale = parseInt($(this).data("single-bar-used"));
        if (scale > maxScale) {
          maxScale = scale;
        }
      });
      return [0, maxScale];
    };

    if (self.jqueryElement.data("single-bar-color-scale-domain")) {
      self.data.colorScaleDomain =
        self.jqueryElement.data("single-bar-color-scale-domain");
    } else if (self.isAutoScaling()) {
      // Dynamically set scale based on biggest value
      self.data.colorScaleDomain = self.autoScale();
    } else {
      self.data.colorScaleDomain = [0, 100];
    }
    if (self.jqueryElement.data("single-bar-color-scale-range")) {
      self.data.colorScaleRange =
        self.jqueryElement.data("single-bar-color-scale-range");
    } else {
      self.data.colorScaleRange = ["#000000", "#0000FF"];
    }
    // Tooltips data
    self.data.popupAverage = self.jqueryElement.data("popup-average");
    self.data.popupFree = self.jqueryElement.data("popup-free");
    self.data.popupUsed = self.jqueryElement.data("popup-used");

    // Orientation of the Bar chart
    self.data.orientation = self.jqueryElement.data("single-bar-orientation");

    // Refresh method
    self.refresh = function (){
      self.chartClass.render(self.htmlElement, self.data);
    };
  },
  BaseComponent: function(data){
    "use strict";

    var self = this;

    self.data = data;

    self.w = data.width;
    self.h = data.height;
    self.lvlCurve = 3;
    self.bkgrnd = "#F2F2F2";
    self.frgrnd = "grey";
    self.colorScaleMax = 25; // Is this used? /lregebro

    self.percentageUsed = data.percentageUsed;
    self.totalUsedPerc = 0;
    self.usedpx = data.usedpx;
    self.percentageAverage = data.percentageAverage;
    self.tooltipUsedContents = data.tooltipUsedContents;

    // set scales
    self.usageColor = d3.scale.linear()
      .domain(data.colorScaleDomain)
      .range(data.colorScaleRange);

    // return true if it renders used percentage multiple in one chart
    self.usedMulti = function (){
      return ($.isArray(self.percentageUsed));
    };

    // deals with percentage if there should be multiple in one chart
    self.usedMultiIterator = 0;
    self.percentageUsedValue = function(){
      if (self.usedMulti()){
        return self.percentageUsed[self.usedMultiIterator];
      } else {
        return self.percentageUsed;
      }
    };
    // deals with html tooltips if there should be multiple in one chart
    self.tooltipUsedValue = function (){
      if (self.usedMulti()){
        return self.tooltipUsedContents[self.usedMultiIterator];
      } else {
        return "";
      }
    };

    // return true if it chart is oriented horizontally
    self.horizontalOrientation = function (){
      return (self.data.orientation === "horizontal");
    };

  },
  UsedComponent: function(baseComponent){
    "use strict";

    var self = this;
    self.baseComponent = baseComponent;

    // FIXME would be good to abstract all attributes and resolve orientation inside
    if (baseComponent.horizontalOrientation()){
      // Horizontal Bars
      self.y = 0;
      self.x = baseComponent.totalUsedPerc + "%";
      self.width = 0;
      self.height = baseComponent.h;
      self.transitionAttr = "width";
      self.transitionValue = baseComponent.percentageUsedValue() + "%";
    } else { // Vertical Bars
      self.y = baseComponent.h;
      self.x = 0;
      self.width = baseComponent.w;
      self.height = baseComponent.percentageUsedValue() + "%";
      self.transitionAttr = "y";
      self.transitionValue = 100 - baseComponent.percentageUsedValue() + "%";
    }

    self.append = function(bar, tooltip){
      var usedComponent = self;

      bar.append("rect")
        .attr("class", "usedbar")
        .attr("y", usedComponent.y)
        .attr("x", usedComponent.x)
        .attr("width", usedComponent.width)
        .attr("height", usedComponent.height)
        //.attr("rx", baseComponent.lvlCurve)
        //.attr("ry", baseComponent.lvlCurve)
        .style("fill", baseComponent.usageColor(baseComponent.percentageUsedValue()))
        .style("stroke", "#bebebe")
        .style("stroke-width", 0)
        .attr("d", baseComponent.percentageUsedValue())
        .attr("popup-used", baseComponent.tooltipUsedValue())
        .on("mouseover", function(){
          if ($(this).attr("popup-used")){
            tooltip.html($(this).attr("popup-used"));
          }
          tooltip.style("visibility", "visible");})
        .on("mousemove", function(event){tooltip.style("top",
          (event.pageY - 10) + "px").style("left", (event.pageX + 10) + "px");})
        .on("mouseout", function(){tooltip.style("visibility", "hidden");})
        .transition()
          .duration(500)
          .attr(usedComponent.transitionAttr, usedComponent.transitionValue);
    };
  },
  AverageComponent: function(baseComponent){
    "use strict";

    var self = this;
    self.baseComponent = baseComponent;

    // FIXME would be good to abstract all attributes and resolve orientation inside
    if (baseComponent.horizontalOrientation()){
      // Horizontal Bars
      self.y = 1;
      self.x = 0;
      self.width = 1;
      self.height = baseComponent.h;
      self.transitionAttr = "x";
      self.transitionValue = baseComponent.percentageAverage + "%";
    } else { // Vertical Bars
      self.y = 0;
      self.x = 0;
      self.width = baseComponent.w;
      self.height = 1;
      self.transitionAttr = "y";
      self.transitionValue = 100 - baseComponent.percentageAverage + "%";
    }

    self.append = function(bar, tooltip){
      var averageComponent = self;

      bar.append("rect")
        .attr("y", averageComponent.y)
        .attr("x", averageComponent.x)
        .attr("class", "average")
        .attr("height", averageComponent.height)
        .attr("width", averageComponent.width)
        .style("fill", "black")
        .on("mouseover", function(){tooltip.style("visibility", "visible");})
        .on("mousemove", function(event){tooltip.style("top",
          (event.pageY - 10) + "px").style("left", (event.pageX + 10) + "px");})
        .on("mouseout", function(){tooltip.style("visibility", "hidden");})
        .transition()
          .duration(500)
          .attr(averageComponent.transitionAttr, averageComponent.transitionValue);
    };
  },
  /* TODO rewrite below as components */
  /* FIXME use some pretty tooltip from some library we will use
   * this one is just temporary */
  appendTooltip: function(tooltip, htmlContent){
    "use strict";

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
      .html(htmlContent);
  },
  appendUnused: function(bar, baseComponent, tooltipFree){
    "use strict";

    bar.append("rect")
      .attr("y", 0)
      .attr("width", baseComponent.w)
      .attr("height", baseComponent.h)
      .attr("rx", baseComponent.lvlCurve)
      .attr("ry", baseComponent.lvlCurve)
      .style("fill", baseComponent.bkgrnd)
      .style("stroke", "#e0e0e0")
      .style("stroke-width", 1)
      .on("mouseover", function(){tooltipFree.style("visibility", "visible");})
      .on("mousemove", function(event){tooltipFree.style("top",
        (event.pageY - 10) + "px").style("left", (event.pageX + 10) + "px");})
      .on("mouseout", function(){tooltipFree.style("visibility", "hidden");});
  },
  // TODO This have to be enhanced, so this library can replace jtomasek capacity charts
  appendText: function(bar, baseComponent, tooltip){
    "use strict";

    bar.append("text")
      .text("FREE")
      .attr("y", baseComponent.h / 2)
      .attr("x", 3)
      .attr("dominant-baseline", "middle")
      .attr("font-size", 13)
      .on("mouseover", function(){tooltip.style("visibility", "visible");})
      .on("mousemove", function(event){tooltip.style("top",
        (event.pageY - 10) + "px").style("left", (event.pageX + 10) + "px");})
      .on("mouseout", function(){tooltip.style("visibility", "hidden");})
      .transition()
        .duration(500)
        .attr("x", function() {
          // FIXME when another panel is active, this page is hidden and usedpx return 0
          // text is then badly positioned, quick fix will be to refresh charts when panel
          // is switched. Need to find better solution.
          if (baseComponent.totalUsedPerc > 90 && baseComponent.usedpx > 25) {
            return baseComponent.usedpx - 20;
          } else {
            return baseComponent.usedpx + 20;
          }
        });
  },
  appendBorder: function(bar){
    "use strict";

    bar.append("rect")
      .attr("x", 0)
      .attr("y", 0)
      .attr("height", "100%")
      .attr("width", "100%")
      .style("stroke", "#bebebe")
      .style("fill", "none")
      .style("stroke-width", 1);
  },
  //  INIT
  init: function() {
    "use strict";

    var self = this;
    this.singleBars = $("div[data-single-bar-used]");

    this.singleBars.each(function() {
      self.refresh(this);
    });
  },
  refresh: function(htmlElement){
    "use strict";

    var chart = new this.SingleBarChart(this, htmlElement);
    // FIXME save chart objects somewhere so I can use them again when
    // e.g. I am swithing tabs, or if I want to update them
    // via web sockets
    // this.charts.add_or_update(chart)
    chart.refresh();
  },
  render: function(htmlElement, data) {
    "use strict";

    // var jqueryElement = $(htmlElement);

    // Initialize baseComponent
    var baseComponent = new this.BaseComponent(data);

    // Bar
    var barHtml = d3.select(htmlElement);

    // Tooltips
    var tooltipAverage = barHtml.append("div");
    if (data.popupAverage) {
      tooltipAverage = this.appendTooltip(tooltipAverage, data.popupAverage);
    }
    var tooltipFree = barHtml.append("div");
    if (data.popupFree) {
      tooltipFree = this.appendTooltip(tooltipFree, data.popupFree);
    }
    var tooltipUsed = barHtml.append("div");
    if (data.popupUsed)  {
      tooltipUsed = this.appendTooltip(tooltipUsed, data.popupUsed);
    }
    // append layout for bar chart
    var bar = barHtml.append("svg:svg")
      .attr("class", "chart")
      .attr("width", baseComponent.w)
      .attr("height", baseComponent.h)
      .style("background-color", "white")
      .append("g");
    var usedComponent;

    // append Unused resources Bar
    this.appendUnused(bar, baseComponent, tooltipFree);

    if (baseComponent.usedMulti()){
      // If Used is shown as multiple values in one chart
      for (var i = 0; i < baseComponent.percentageUsed.length; ++i) {
        // FIXME write proper iterator
        baseComponent.usedMultiIterator = i;

        // Use general tooltip, content of tooltip will be changed
        // by inner used compoentnts on their hover
        tooltipUsed = this.appendTooltip(tooltipUsed, "");

        // append used so it will be shown as multiple values in one chart
        usedComponent = new this.UsedComponent(baseComponent);
        usedComponent.append(bar, tooltipUsed);

        // append Used resources to Bar
        baseComponent.totalUsedPerc += baseComponent.percentageUsedValue();
      }

      // append Text to Bar
      this.appendText(bar, baseComponent, tooltipFree);

    } else {
      // used is show as one value it the chart
      usedComponent = new this.UsedComponent(baseComponent);
      usedComponent.append(bar, tooltipUsed);

      // append average value to Bar
      var averageComponent = new this.AverageComponent(baseComponent);
      averageComponent.append(bar, tooltipAverage);
    }
    // append border of whole Bar
    this.appendBorder(bar);
  }
};


horizon.addInitFunction(function () {
  "use strict";

  horizon.d3SingleBarChart.init();
});
