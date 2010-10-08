require.def('design/chart', ['design/form', 'lib/highcharts'], function(form) {
     var UNSELECTED_COLOR     = "#8E8F93";
     var SELECTED_COLOR       = "#99BDF1";
     var EXCLUDE_COLOR        = "#EE3A43";
     var INCLUDE_COLOR        = "#99BDF1";
     var ALTERNATE_GRID_COLOR = "#FDFFD5";
     var MINIMUM_SLICE = 0.07;
     
    var map_data_to_display = function(choices){
        var map = {};
        $.each(choices, function(index,element){
            map[element[0]]=element[1];
        });
        return map;
    };
    
    var map_display_to_data = function(choices){
        var map = {};
        $.each(choices, function(index,element){
            map[element[1]]=element[0];
        });
        return map;
    };
    
    // Map used to convert array operators for the null boolean type;
    var nb_plural_to_singular_map = {"in":"exact", "-in":"-exact"};
    var nb_singular_to_plural_map = {"exact":"in", "-exact":"-in"}; 
     
     
     var getPieChart = function(view, concept_id, $location){
         // HighCharts cannot handle boolean values in the coordinates
         var map = map_data_to_display(view.data.choices);
         var unmap = map_display_to_data(view.data.choices);
         
         var negated = false;
         var $range_form = form.Form({fields:[{ datatype: "string",
                                                name: view.data.name,
                                                choices:view.data.choices,
                                                pk: view.data.pk}]}, concept_id);
         
         // The graph serves the purpose of multiple selector.
         $range_form.find('select[multiple]').hide();
         
         // Highcharts does not less us pass in null and true and false for coords
         $.each(view.data.coords, function(index,element){
                         view.data.coords[index][0] = map[view.data.coords[index][0]];
         });
         
         // We only use pie charts for series with <= 3 choices.
         // Verify that no one piece is less than MINIMUM_SLICE of
         // the whole thing / NOTE this doesn't work great yet
         var coords = view.data.coords;
         var data_store = {};
         $.each(coords, function(index,element){
             data_store[element[0]] = element[1];
         });
         
         var sum = 0;
         $.each(coords, function(index, element){
            sum = sum + element[1];
         });
         var min_slice_width = sum * MINIMUM_SLICE;
         $.each(coords, function(index,element){
            if (element[1] < min_slice_width){
                element[1] = min_slice_width;
            }
         });
            
         var $chartDiv = $('<div class="chart"></div>');
         $chartDiv.css("display","none");
         $location && $location.append($chartDiv);
         var selected = [];
         
         var notify = function(){
             $chartDiv.trigger("ElementChangedEvent", [{name:concept_id+"_"+view.data.pk, value:selected}]);
         };
         
         $chartDiv.bind("UpdateElementEvent", function(evt, element){
             if (element.name === concept_id+"_"+view.data.pk){
                 selected = element.value;
             }else { 
                 if (element.name === concept_id+"_"+view.data.pk+"_operator" && element.value==="in"){
                     negated = false;
                 }else{
                     negated = true;
                 }
             }
             // Gain focus will take care of updating graph
             // Tell embedded form
             $range_form.triggerHandler(evt,[element]);
         });
         
         var chart = new Highcharts.Chart({
             chart: {
                 marginBottom:50,
                 renderTo: $chartDiv.get(0),
                 defaultSeriesType: 'pie',
                 zoomType:''
             },
             tooltip:{
                 formatter:function(){
                     return "" + data_store[this.point.name];
                 }
             },
             plotOptions:{
                 series:{
                     events: {
                         click : function(event) {
                             var category = event.point.category || event.point.name;               
                             var index = $.inArray(unmap[category],selected);
                             if (index === -1) {
                                 if (negated){
                                     event.point.update({color:EXCLUDE_COLOR});
                                 }else{
                                     event.point.update({color:SELECTED_COLOR});
                                 }
                                 selected.push(unmap[category]);
                             }else{
                                 event.point.update({color:UNSELECTED_COLOR});
                                 selected.splice(index,1);
                             }
                             notify();
                             chart.hoverPoint = event.point;
                             chart.hoverSeries = this;
                         }
                     }
                 },
                 pie:{
                     dataLabels: {
                         enabled: true,
                         formatter: function() {
                                        return this.point.name;
                                    }
                     },
                     borderWidth: 3,
                     allowPointSelect: false,
                     cursor: "pointer",
                     enableMouseTracking: true,
                     stickyTracking: false,
                
                     states:{
                         hover:{
                             brightness: 0
                         }
                     }
                 }
             },
         
             credits:{
                 enabled: false
             },
             legend:{
                 enabled: false
             },
              title: {
                  text: null
              },
             series: [{
                type: 'pie',
                name: view.data.title,
                data: view.data.coords
             }]
         });
        $chartDiv.prepend($range_form);
        
        function updateChart(){
            // Rotated text does not show up without this in 
            // ie 8 and ie 7
            $.map(chart.series[0].data, function(element,index){
                   var category = element.name || element.category;
                   if ($.inArray(unmap[category], selected) !==-1){
                       if (negated){
                           element.update({color:EXCLUDE_COLOR});
                       }else{
                           element.update({color:SELECTED_COLOR});
                       }
                   }else{
                       element.update({color:UNSELECTED_COLOR});
                   }
                   $(element.tracker.element).mouseover();
                   $(element.tracker.element).mouseout();
             });

            chart.xAxis[0].isDirty = true;
            chart.yAxis[0].isDirty = true;
            chart.isDirty = true;
            chart.series[0].isDirty = true;
            chart.redraw();
        }
        
        $range_form.bind("ElementChangedEvent",function(evt,value){
               // We don't care about null values here because it means
               // the item was hidden
               if (value.value === null) return;
               if (value.value === "in"){
                   negated = false;
               }else{
                   negated = true;
               }
               updateChart();
        });
       
        $chartDiv.bind("GainedFocusEvent", function(evt){
            $('input,select',$chartDiv).change();
        });
         
        $chartDiv.bind("UpdateDSEvent", function(evt, ds){
             selected = ds[concept_id+  "_"+view.data.pk] || [];
             negated = ds[concept_id + "_"+view.data.pk + "_operator"] === "-in";
             $range_form.triggerHandler(evt,[ds]);
        });
        return $chartDiv;
     };
 
     var getBarChart = function(view, concept_id, $location) {
         // HighCharts cannot handle boolean values in the coordinates
         var map = map_data_to_display(view.data.choices);
         var unmap = map_display_to_data(view.data.choices);
   
         var negated = false;
         var $range_form = form.Form({fields:[{ datatype: "string",
                                                name: view.data.name,
                                                choices:view.data.choices,
                                                pk: view.data.pk}]}, concept_id);
         
         // The graph serves the purpose of multiple selector.
         $range_form.find('select[multiple]').hide();

         $range_form.find("input").css("margin","10px"); //TODO should not be here
         var $chartDiv = $('<div class="chart"></div>');
         $chartDiv.css("display","none");
         $location && $location.append($chartDiv);
         var selected = [];
         
         var notify = function(){
             $chartDiv.trigger("ElementChangedEvent", [{name:concept_id+"_"+view.data.pk, value:selected}]);
         };

         
         var chart = new Highcharts.Chart({
            chart: {
               marginLeft:100,
               marginBottom: view.data.coords.length > 6 ? 100 : 50,
               renderTo: $chartDiv.get(0),
               defaultSeriesType: 'column',
               zoomType:'',
               events:{
                   // Both the load and redraw functions handle making sure the datalabels are 
                   // clickable for the bars and that they are the proper color
                   redraw: function(event){
                        for (var index = 0; index < this.series[0].data.length; index++){
                             var col = this.series[0].data[index];
                                                           
                             $(col.dataLabel.element).attr("fill", col.color);//chrome/firefox
                             $(col.dataLabel.element).css("color", col.color);//ie
                             $(col.dataLabel.element).hover(function(event){
                                 $(this).css("cursor","pointer");
                             }, function(event){
                                 $(this).css("cursor","");
                             });
                         
                             $(col.dataLabel.element).click(function(c){
                                 return (function(event){
                                          c.series.chart.hoverPoint = c;
                                          c.series.chart.isDirty = true;
                                          var index = $.inArray(unmap[c.category], selected);
                                          if (index === -1) {
                                              if (negated){
                                                  c.update({color:EXCLUDE_COLOR});
                                              }else{
                                                  c.update({color:SELECTED_COLOR});
                                              }
                                              selected.push(unmap[c.category]);
                                          }else{
                                              c.update({color:UNSELECTED_COLOR});
                                              selected.splice(index,1);
                                          }
                                          notify();
                                     });            
                             }(col));
                        }
                   },
                   load: function(){
                       for (var index = 0; index < this.series[0].data.length; index++){
                             var col = this.series[0].data[index];
                             $(col.dataLabel.element).hover(function(event){
                                 $(this).css("cursor","pointer");
                             }, function(event){
                                 $(this).css("cursor","");
                             });

                             $(col.dataLabel.element).click(function(c){

                                 return (function(event){
                                        c.series.chart.hoverPoint = c;
                                        c.series.chart.isDirty = true;
                                        var index = $.inArray(unmap[c.category], selected);
                                        if (index === -1) {
                                            
                                            if (negated){
                                                 $(c.dataLabel.element).css("color", EXCLUDE_COLOR);
                                                c.update({color:EXCLUDE_COLOR});
                                            }else{
                                                 $(c.dataLabel.element).css("color", SELECTED_COLOR);
                                                c.update({color:SELECTED_COLOR});
                                            }
                                            selected.push(unmap[c.category]);
                                        }else{
                                            $(c.dataLabel.element).css("color", UNSELECTED_COLOR);
                                            c.update({color:UNSELECTED_COLOR});
                                            selected.splice(index,1);
                                        }
                                   });                       
                             }(col));
                        }
                   }
               }
            },
            plotOptions:{
                series:{
                    events: {
                        click : function(event) {                
                             var category = event.point.category || event.point.name;               
                             var index = $.inArray(unmap[category],selected);
                             if (index === -1) {
                                 if (negated){
                                       event.point.update({color:EXCLUDE_COLOR});
                                 }else{
                                       event.point.update({color:SELECTED_COLOR});
                                 }
                                 selected.push(unmap[category]);
                             }else{
                                 event.point.update({color:UNSELECTED_COLOR});
                                 selected.splice(index,1);
                             }
                             chart.hoverPoint = event.point;
                             chart.hoverSeries = this;
                             notify();
                        }
                    }  
                },
                column:{
                    dataLabels: {
                        enabled: true
                    },
                    allowPointSelect:false,
                    cursor:"pointer",
                    enableMouseTracking:true,
                    stickyTracking:false
                }
            },
            credits:{
                enabled:false
            },
            legend:{
                enabled:false
            },
            title: {
               text: null
            },
            tooltip:{
                   formatter:function(){
                       return this.point.category + ", " + this.y;
                   }
            },
            xAxis: {
               categories: $.map(view.data.coords, function(element, index){
                  return map[element[0]]; 
               }),
               title: {
                   text: view.data.xaxis,
                   margin: view.data.coords.length > 6 ? 90 : 50
               },
               labels:{
                   align: view.data.coords.length > 6 ? 'left' : 'center',
                   y: view.data.coords.length > 6 ? 10 : 20,
                   rotation: view.data.coords.length > 6 ? 50 : 0,
                   formatter: function(){
                       // Make words appear on separate lines unless they are rotated
                       var value = this.value;
                       if (view.data.coords.length > 6) { // If there are more than 6 categories, they will be rotated
                           if (value.length > 20){
                               value = value.substr(0,18)+"..";
                           }
                       }else {
                           // Values aren't rotated, put one word per line
                           value = this.value.split(" ").join("<br/>");
                       }
                       
                       return value;
                   }
               }
            },
            yAxis: {
               min:0,
               title: {
                  text: view.data.yaxis
               },
               labels:{
                    rotation: 45
               }
               
            },
            series: [{
               name: view.data.title,
               data: $.map(view.data.coords, function(element, index){
                         return element[1]; 
                     })
             }]
         });
         
         $chartDiv.prepend($range_form);
         
         function updateChart(){
                $.map(chart.series[0].data, function(element,index){
                    if ($.inArray(unmap[element.category], selected) !==-1){
                        if (negated){
                            element.update({color:EXCLUDE_COLOR});
                        }else{
                            element.update({color:SELECTED_COLOR});    
                        }
                    }else{
                        element.update({color:UNSELECTED_COLOR});
                    }
                    // This is a hack to fix a bug in ie7 where bars that
                    // have been moused over, vanish if the view is taken off
                    // screen and then put back.
                    $(element.tracker.element).mouseover();
                    $(element.tracker.element).mouseout();
                 });
         
                 // Rotated text does not show up in ie8 and ie7 
                 // when the graph is inserted dynamically without this
                 chart.xAxis[0].isDirty = true;
                 chart.yAxis[0].isDirty = true;
                 chart.isDirty = true;
                 chart.series[0].isDirty = true;
                 chart.redraw();
         }
         
         $range_form.bind("ElementChangedEvent", function(evt, item){
            // We don't care about null values here because it means
            // the item was hidden
            if (item.value === null) return;
            if (item.value ==="in"){
                negated = false;
            }else{
                negated = true;
            }
            updateChart();
         });
         
         // AvocadoClient event listners
         $chartDiv.bind("GainedFocusEvent", function(evt){
            $('input,select',$chartDiv).change();
         });
         
         $chartDiv.bind("UpdateDSEvent", function(evt, ds){
            selected =  ds[concept_id+"_"+view.data.pk] || [];

            negated = ds[concept_id + "_"+view.data.pk + "_operator"] === "-in";
            $range_form.triggerHandler(evt,[ds]);
         });

         $chartDiv.bind("UpdateElementEvent", function(evt, element){
               if (element.name === concept_id+"_"+view.data.pk){
                   selected = element.value;
               }else if (element.name === concept_id + "_"+view.data.pk + "_operator"){
                   if (element.value==="in"){
                      negated = false;
                   }else{
                      negated = true;
                   }
               }
               // Gained focus will take care of actually changing the colors for us
               $range_form.triggerHandler(evt,[element]);
         });
         
         return $chartDiv;
     };    
 
     var getLineChart = function(view, concept_id, $location) {
         var $range_form = form.Form({fields:[view.data]}, concept_id);

         $range_form.find("input").css("margin","10px");
         var $chartDiv = $('<div class="chart"></div>');
         $chartDiv.css("display","none");
         $location && $location.append($chartDiv);
         var chart = new Highcharts.Chart({
            chart: {
               marginBottom:50,
               renderTo: $chartDiv.get(0),
               defaultSeriesType: 'line',
               zoomType:'x',
               events:{
                   selection: function(event){
                       var color = $range_form.find("select[name*=operator]").val() === "-range" ? EXCLUDE_COLOR : INCLUDE_COLOR;
                       var extremes = this.xAxis[0].getExtremes();

                       var min = event.xAxis[0].min;
                       var max = event.xAxis[0].max;

                       min = min < extremes.min ? extremes.min : min;
                       max = max > extremes.max ? extremes.max : max;
                       min = parseFloat(min).toFixed(1);// TODO how are we going to handle this if they are fractions
                       max = parseFloat(max).toFixed(1);// TODO properly calculate extremes 

                       // Set the new values in the form and notify Avocado
                       $("input[name*=input0]", $range_form).val(min).change();
                       $("input[name*=input1]", $range_form).val(max).change();

                       // We want the graph to reflect the possible operators

                       this.xAxis[0].isDirty = true;
                       chart.isDirty = true;
                       this.xAxis[0].redraw();
                       chart.redraw();
                       event.preventDefault();
                   },
                   click: function clickEvent(event){
                       if (chart.options.chart.zoomType){ // If select is on we don't care about click
                           return; 
                       }
                       var extremes = this.xAxis[0].getExtremes();

                       var min = event.xAxis[0].value;

                       min = min < extremes.min ? extremes.min : min;
                       min = parseFloat(min).toFixed(1);// TODO how are we going to handle this if they are fractions

                       // Set the new values in the form and notify Avocado
                       $("input[name*=input0]", $range_form).val(min).change();
                         this.xAxis[0].isDirty = true;
                         chart.isDirty = true;
                         this.xAxis[0].redraw();
                         chart.redraw();
                   }
               }
            },
            tooltip:{
                formatter:function() {
                   return "" + this.y;
                }
            },
            credits:{
                enabled:false
            },
            legend:{
                enabled:false
            },
            title: {
               text: view.data.title
            },
            xAxis: {
                min:0,
                title: {
                    text: view.data.xaxis
                },
                labels:{
                      align:"center",
                      y:20
                }
            },
            yAxis: {
                min:0,
                title: {
                   style: {
                       fontWeight: 'bold'
                   },
                   text:  view.data.yaxis,
                   rotation : 270
                },
                labels:{
                   rotation:45
                }
            },
            series: [{
                name: view.data.title,
                data: view.data.coords
            }],
            plotOptions: {
                line:{
                    animation: true
                },
                series:{
                    point:{
                        events:{
                            click: function clickEvent(event){
                                  if (chart.options.chart.zoomType){ // If select is on we don't care about click
                                      return; 
                                  }
                                  var extremes = chart.xAxis[0].getExtremes();

                                  var min = this.x;

                                  min = min < extremes.min ? extremes.min : min;

                                  min = parseFloat(min).toFixed(1);// TODO how are we going to handle this if they are fractions

                                  // Set the new values in the form and notify Avocado
                                  $("input[name*=input0]", $range_form).val(min).change();
                                    chart.xAxis[0].isDirty = true;
                                    chart.isDirty = true;
                                    chart.xAxis[0].redraw();
                                    chart.redraw();
                              }
                        }
                    }
                }
            }
         });

         var extremes = chart.xAxis[0].getExtremes();

         // Create handler for updating graph whnen user changes min and max values
         // in the form
         var manual_field_handler = function(event){
             var color = null;
             // Depending on the value of the operator, clicking on the graph
             // will have a different behavior
             // For example, range and exclude:range will allow 
             // selecting a region of the graph.
             // All other operators will insert a line on click.
             // the lt,gt,lte,gte, will insert a box after the user 
             // clicks to indicate the selected region.
             // The exact operators will insert a line.

             var options = chart.options;
             var min = parseFloat($("input[name*=input0]", $range_form).val()).toFixed(1);
             var max = parseFloat($("input[name*=input1]", $range_form).val()).toFixed(1);
             
             switch($range_form.find("select[name*=operator]").val()) {
                 case "range": 
                     color = INCLUDE_COLOR;
                 case "-range":
                     color =  color || EXCLUDE_COLOR; // did we drop through from range?
                     if (options.chart.zoomType !== "x"){
                             $range_form.detach();
                             chart.destroy();
                             options.chart.zoomType = "x";
                             options.plotOptions.line.animation = false;
                             chart = new Highcharts.Chart(options);
                             $chartDiv.append($range_form);
                     }
                     chart.xAxis[0].removePlotBand();
                     if (min && max){     
                            chart.xAxis[0].addPlotBand({
                              from: min,
                              to: max,
                              color:color
                            });
                     }
                     $chartDiv.trigger("ShowDependentsEvent");
                     break;
                 case "lt":
                     color = INCLUDE_COLOR;
                     if (options.chart.zoomType !== ""){
                         $range_form.detach();
                         chart.destroy();
                         options.chart.zoomType = "";
                         options.plotOptions.line.animation = false;
                         chart = new Highcharts.Chart(options);
                         $chartDiv.append($range_form);
                     }
                     chart.xAxis[0].removePlotBand();
                     
                     if (min){
                         chart.xAxis[0].addPlotLine({
                                     value: min,
                                     color: EXCLUDE_COLOR,
                                     width: 3
                         });
                         chart.xAxis[0].addPlotBand({
                              from: extremes.min,
                              to: min,
                              color:color
                         });
                     }
                     $chartDiv.trigger("ShowDependentsEvent");
                     break;
                 case "gt":
                     color = INCLUDE_COLOR;
                     if (options.chart.zoomType !== ""){
                         $range_form.detach();
                         chart.destroy();
                         options.chart.zoomType = "";
                         options.plotOptions.line.animation = false;
                         chart = new Highcharts.Chart(options);
                         $chartDiv.append($range_form);
                     }
                     chart.xAxis[0].removePlotBand();
                     
                     if (min){
                         chart.xAxis[0].addPlotLine({
                                     value: min,
                                     color: EXCLUDE_COLOR,
                                     width: 3
                         });
                         chart.xAxis[0].addPlotBand({
                              from: min,
                              to: extremes.max,
                              color:color
                         });
                     }
                     $chartDiv.trigger("ShowDependentsEvent");
                     break;
                 case "lte":
                     color = INCLUDE_COLOR;
                     if (options.chart.zoomType !== ""){
                         $range_form.detach();
                         chart.destroy();
                         options.chart.zoomType = "";
                         options.plotOptions.line.animation = false;
                         chart = new Highcharts.Chart(options);
                         $chartDiv.append($range_form);
                     }
                     chart.xAxis[0].removePlotBand();
                     
                     if (min){
                         chart.xAxis[0].addPlotBand({
                              from: extremes.min,
                              to: min,
                              color:color
                         });
                     }
                     $chartDiv.trigger("ShowDependentsEvent");
                     break;
                 case "gte":
                     color = INCLUDE_COLOR;
                     if (options.chart.zoomType !== ""){
                         $range_form.detach();
                         chart.destroy();
                         options.chart.zoomType = "";
                         options.plotOptions.line.animation = false;
                         chart = new Highcharts.Chart(options);
                         $chartDiv.append($range_form);
                     }
                     chart.xAxis[0].removePlotBand();
                     
                     if (min){
                         chart.xAxis[0].addPlotBand({
                              from: min,
                              to: extremes.max,
                              color:color
                         });
                     }
                     $chartDiv.trigger("ShowDependentsEvent");
                     break;
                 case "exact":
                     color = INCLUDE_COLOR;
                     if (options.chart.zoomType !== ""){
                         $range_form.detach();
                         chart.destroy();
                         options.chart.zoomType = "";
                         options.plotOptions.line.animation = false;
                         chart = new Highcharts.Chart(options);
                         $chartDiv.append($range_form);
                     }
                     chart.xAxis[0].removePlotBand();
                     
                     if (min){
                         chart.xAxis[0].addPlotLine({
                                     value: min,
                                     color: INCLUDE_COLOR,
                                     width: 3
                         });
                     }
                     $chartDiv.trigger("ShowDependentsEvent");
                     break;
                 case "-exact":
                     color = INCLUDE_COLOR;
                     if (options.chart.zoomType !== ""){
                         $range_form.detach();
                         chart.destroy();
                         options.chart.zoomType = "";
                         options.plotOptions.line.animation = false;
                         chart = new Highcharts.Chart(options);
                         $chartDiv.append($range_form);
                     }
                     chart.xAxis[0].removePlotBand();
                     
                     if (min){
                         chart.xAxis[0].addPlotLine({
                                     value: min,
                                     color: EXCLUDE_COLOR,
                                     width: 3
                         });
                     }
                     $chartDiv.trigger("ShowDependentsEvent");
                     break;
                 case "isnull":
                     color = EXCLUDE_COLOR;
                     if (options.chart.zoomType !== ""){
                         $range_form.detach();
                         chart.destroy();
                         options.chart.zoomType = "";
                         options.plotOptions.line.animation = false;
                         chart = new Highcharts.Chart(options);
                         $chartDiv.append($range_form);
                     }
                     chart.xAxis[0].removePlotBand();
                     chart.xAxis[0].addPlotLine({
                                from: extremes.min,
                                to: extremes.max,
                                color:color
                     });
                     $chartDiv.trigger("HideDependentsEvent");
                     break;
                 case "-isnull":
                     if (options.chart.zoomType !== ""){
                         $range_form.detach();
                         chart.destroy();
                         options.chart.zoomType = "";
                         options.plotOptions.line.animation = false;
                         chart = new Highcharts.Chart(options);
                         $chartDiv.append($range_form);
                     }
                     $chartDiv.trigger("ShowDependentsEvent");
                     chart.xAxis[0].removePlotBand();
                     break;
             }

             chart.xAxis[0].isDirty = true;
             chart.redraw();
         };
         
         // Listen for changes in the form and make the chart reflect
         $range_form.bind("ElementChangedEvent", manual_field_handler);
         
         // Add the form to the top of this chart widget
         $chartDiv.append($range_form);
     
         // By default select the middle 1/3 of the chart
         var xrange = extremes.max - extremes.min;
         var third = (1/3) * xrange;
         
         // Set the initial middle selected range in the form and in the graph.
         // TODO Set these using events so as not to need to know internals.
         $("input[name*=input0]", $range_form).val((extremes.min+third).toFixed(1));
         $("input[name*=input1]", $range_form).val((extremes.min+2*third).toFixed(1));
         
         // AvocadoClient Event Listeners
         
         // Listen for updates to the datasource from the framework
         // We have an embedded form in this chart, which is really
         // the only thing that changes the datasource. The graph 
         // monitors and changes the form
         $chartDiv.bind("UpdateDSEvent", function(evt, ds){
             // pass the datasource to the embedded form
             $range_form.triggerHandler(evt,[ds]);
         });
         
         $chartDiv.bind("UpdateElementEvent", function(evt, element) {
             // Use triggerHandler here because otherwise it will bubble back up
             // the surround container (this object) and start an endless loop.
             $range_form.triggerHandler(evt,[element]);
             manual_field_handler(null);
         });

         $chartDiv.bind("GainedFocusEvent", function(evt){
             // TODO, remove this
             $('input,select',$chartDiv).change();
             chart.xAxis[0].isDirty = true;
             chart.yAxis[0].isDirty = true;          
             chart.isDirty = true;
             chart.redraw();
         });
         
         return $chartDiv;
     };
     
     return {
         getBarChart: getBarChart,
         getLineChart: getLineChart,
         getPieChart: getPieChart
     };
});
