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

horizon.Capacity = {
  capacity_bars: [],

  //  Determines the capacity bars to be used for capacity display.
  init: function() {
    this.capacity_bars = $('div[data-chart-type="capacity_bar_chart"]');

    // Draw the capacity bars
    this._initialCreation(this.capacity_bars);
  },


  /*
    Create a new d3 bar and populate it with the current amount used,
    average used, and percentage label
  */
  drawUsed: function(element, used_perc, used_px, average_perc) {
    var w= "100%";
    var h= 15;
    var lvl_curve= 3;
    var bkgrnd= "#F2F2F2";
    var frgrnd= "grey";
    var usage_color = d3.scale.linear()
                              .domain([0, 50, 75, 90, 100])
                              .range(["#669900", "#669900", "#FF9900", "#FF3300", "#CC0000"]);

    // Horizontal Bars
    var bar = d3.select("#"+element).append("svg:svg")
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
      .attr("rx", lvl_curve)
      .attr("ry", lvl_curve)
      .style("fill", bkgrnd)
      .style("stroke", "#bebebe")
      .style("stroke-width", 1);

    // used resources
    if (used_perc) {
      bar.append("rect")
         .attr("class", "usedbar")
         .attr("y", 0)
         .attr("id", "test")
         .attr("width", 0)
         .attr("height", h)
         .attr("rx", lvl_curve)
         .attr("ry", lvl_curve)
         .style("fill", usage_color(used_perc))
         .style("stroke", "#a0a0a0")
         .style("stroke-width", 1)
         .attr("d", used_perc)
         .transition()
            .duration(500)
            .attr("width", used_perc + "%");
      }

    // average
    if (average_perc) {
      bar.append("rect")
         .attr("y",1)
         .attr("x", 0)
         .attr("class", "average")
         .attr("height", h-2)
         .attr("width", 1)
         .style("fill", "black")
         .transition()
            .duration(500)
            .attr("x", average_perc + "%");
    }

    // used text
    if (used_perc) {
      bar.append("text")
         .text(used_perc + "%")
         .attr("y", 8)
         .attr("x", 3)
         .attr("dominant-baseline", "middle")
         .attr("font-size", 10)
         .transition()
            .duration(500)
            .attr("x", function() {
              // position the percentage label
              if (used_perc > 99 && used_px > 25){
                return used_px - 30;
              } else if (used_px > 25) {
                return used_px - 25;
              } else {
                return used_px + 3;
              }
            });
    }
  },


  // Draw the initial d3 bars
  _initialCreation: function(bars) {
    var scope = this;

    $(bars).each(function(index, element) {
      var progress_element = $(element);

      var capacity_limit = parseInt(progress_element.attr('data-capacity-limit'), 10);
      var capacity_used = parseInt(progress_element.attr('data-capacity-used'), 10);
      var average_used = parseInt(progress_element.attr('data-average-capacity-used'), 10);
      var percentage_used = 0;
      var average_percentage = 0;
      var _used_px = 0;

      if (!isNaN(capacity_limit) && !isNaN(average_used)) {
        average_percentage = ((average_used / capacity_limit) * 100);
      }
      if (!isNaN(capacity_limit) && !isNaN(capacity_used)) {
        percentage_used = Math.round((capacity_used / capacity_limit) * 100);
        _used_px = progress_element.width() / 100 * percentage_used;
      }

      scope.drawUsed($(element).attr('id'), percentage_used, _used_px, average_percentage);
    });
  }
};

horizon.addInitFunction(function () {
  horizon.Capacity.init();
});
