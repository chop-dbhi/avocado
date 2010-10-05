require.def('design/views',  ['design/chart','design/form'], function(chart, form){
    
    

     /**
        Certain types of views are built-into the framework.
        
        We do not have to make external calls to retrieve their code. 
        Control will be passed to the built-in concept code from
        this function
        
      @private 
    */
    function createView(view) {
        // TODO create a base view class and use it here        
        var $view = $('<div class="view"></div>');
        $view.bind("UpdateQueryButtonClicked", function(event){
            $(this).trigger("ConstructQueryEvent");
        });
        $view.bind("UpdateElementEvent", function(evt, element){
            $view.children().trigger("UpdateElementEvent",[element]);
            evt.stopPropagation();
        });
        
        $.each(view.elements, function(index, element) {
            switch (element.type) {
                case 'form':
                    $view.append(form.Form(element,view.concept_id)); 
                    break;
                case 'chart':
                    var datatype = element.data.datatype;
                    var location = undefined; //Modernizr.svg ? undefined : $contentBox;
                    if (datatype === 'number') {
                        $view.append(chart.getLineChart(element, view.concept_id, location)); 
                    } else if (datatype === 'nullboolean'){
                        $view.append(chart.getPieChart(element,  view.concept_id, location));
                    } else{
                        $view.append(chart.getBarChart(element,  view.concept_id, location));
                    }
                    break;
                default:
                    $view.append($('<p>Undefined View!</p>'));                
            }
        });
        
        return $view;
    }
    return { createView: createView};
});