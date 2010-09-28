require.def('design/views',  ['design/chart','design/form'], function(chart, form){
    
    

     /**
        Certain types of views are built-into the framework.
        
        We do not have to make external calls to retrieve their code. 
        Control will be passed to the built-in concept code from
        this function
        
      @private 
    */
    function createView(view, $container) {        
        var result = $('<div class="view"></div>');
        result.bind("UpdateQueryButtonClicked", function(event){
            $(this).trigger("ConstructQueryEvent");
        });
        
        $.each(view.elements, function(index, element) {
            switch (element.type) {
                case 'form':
                    result.append(form.Form(element,view.concept_id)); 
                    break;
                case 'chart':
                    var datatype = element.data.datatype;
                    var location = undefined; //Modernizr.svg ? undefined : $contentBox;
                    if (datatype === 'decimal') {
                        result.append(chart.getLineChart(element, view.concept_id, location)); 
                    } else if (datatype === 'choice') {
                        var len = element.data.coords.length;
                        if (len <= 3) {
                            result.append(chart.getPieChart(element,  view.concept_id, location));
                        } else {
                            result.append(chart.getBarChart(element,  view.concept_id, location));
                        }
                    }
                    break;
                default:
                    result.append($('<p>Undefined View!</p>'));                
            }
        });
        
        // Show the view
        $container.trigger('ViewReadyEvent', [result]);
    }
    return { createView: createView};
});