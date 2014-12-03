/*
  Used for animating and displaying capacity information using
  D3js progress bars.

  Usage:
    In order to have capacity bars that work with this, you need to have a
    DOM structure like this in your Django template:

    <div id="your_capacity_bar_id" class="capacity_bar">
    </div>

    With this capacity bar, you then need to add some data- HTML attributes
    to the div #your_capacity_bar_id. The available data- attributes are:

      data-chart-type="capacity_bar_chart" REQUIRED
          Must be "capacity_bar_chart".

      data-capacity-used="integer" OPTIONAL
          Integer representing the total number used by the user.

      data-capacity-limit="integer" OPTIONAL
          Integer representing the total quota limit the user has. Note this IS
          NOT the amount remaining they can use, but the total original capacity.

      data-average-capacity-used="integer" OPTIONAL
          Integer representing the average usage of given capacity.
*/

/* global $ horizon d3*/
horizon.Capacity = {
  capacityBars: [],

  //  Determines the capacity bars to be used for capacity display.
  init: function() {
    "use strict";

    this.capacityBars = $("div[data-chart-type=\"capacity_bar_chart\"]");

    // Draw the capacity bars
    this.initialCreation(this.capacityBars);
  },


  /*
    Create a new d3 bar and populate it with the current amount used,
    average used, and percentage label
  */
  drawUsed: function(element, usedPerc, usedpx, averagePerc) {
    "use strict";

    var w = "100%";
    var h = 15;
    var lvlCurve = 3;
    var bkgrnd = "#F2F2F2";
    var frgrnd = "#bebebe";
    var usageColor = d3.scale.linear()
                              .domain([0, 50, 75, 90, 100])
                              .range(["#669900", "#669900", "#FF9900", "#FF3300", "#CC0000"]);

    // Horizontal Bars
    var bar = d3.select("#" + element).append("svg:svg")
        .attr("class", "chart")
        .attr("width", w)
        .attr("height", h)
        .style("background-color", "white")
        .append("g");

    // background - unused resources
    bar.append("rect")
      .attr("y", 0)
      .attr("width", w)
      .attr("height", h)
      .attr("rx", lvlCurve)
      .attr("ry", lvlCurve)
      .style("fill", bkgrnd)
      .style("stroke", frgrnd)
      .style("stroke-width", 1);

    // used resources
    if (usedPerc) {
      bar.append("rect")
         .attr("class", "usedbar")
         .attr("y", 0)
         .attr("id", "test")
         .attr("width", 0)
         .attr("height", h)
         .attr("rx", lvlCurve)
         .attr("ry", lvlCurve)
         .style("fill", usageColor(usedPerc))
         .style("stroke", "#a0a0a0")
         .style("stroke-width", 1)
         .attr("d", usedPerc)
         .transition()
            .duration(500)
            .attr("width", usedPerc + "%");
      }

    // average
    if (averagePerc) {
      bar.append("rect")
         .attr("y", 1)
         .attr("x", 0)
         .attr("class", "average")
         .attr("height", h - 2)
         .attr("width", 1)
         .style("fill", "black")
         .transition()
            .duration(500)
            .attr("x", averagePerc + "%");
    }

    // used text
    if (usedPerc) {
      bar.append("text")
         .text(usedPerc + "%")
         .attr("y", 8)
         .attr("x", 3)
         .attr("dominant-baseline", "middle")
         .attr("font-size", 10)
         .transition()
            .duration(500)
            .attr("x", function() {
              // position the percentage label
              if (usedPerc > 99 && usedpx > 25){
                return usedpx - 30;
              } else if (usedpx > 25) {
                return usedpx - 25;
              } else {
                return usedpx + 3;
              }
            });
    }
  },


  // Draw the initial d3 bars
  initialCreation: function(bars) {
    "use strict";

    var scope = this;

    $(bars).each(function(index, element) {
      var progressElement = $(element);

      var capacityLimit = parseInt(progressElement.attr("data-capacity-limit"), 10);
      var capacityUsed = parseInt(progressElement.attr("data-capacity-used"), 10);
      var averageUsed = parseInt(progressElement.attr("data-average-capacity-used"), 10);
      var percentageUsed = 0;
      var averagePercentage = 0;
      var usedpx = 0;

      if (!isNaN(capacityLimit) && !isNaN(averageUsed)) {
        averagePercentage = ((averageUsed / capacityLimit) * 100);
      }
      if (!isNaN(capacityLimit) && !isNaN(capacityUsed)) {
        percentageUsed = Math.round((capacityUsed / capacityLimit) * 100);
        usedpx = progressElement.width() / 100 * percentageUsed;
      }

      scope.drawUsed($(element).attr("id"), percentageUsed, usedpx, averagePercentage);
    });
  }
};

horizon.addInitFunction(function () {
  "use strict";

  horizon.Capacity.init();
});
