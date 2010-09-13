require.def('design/criteria', ['design/templates'], function(templates) {
    var tmpl = $.jqotec(templates.scope_element);
    
    var Criteria = function(criteria_constraint){
        var element = $($.jqote(tmpl, {pk:criteria_constraint.concept_id, description:"Generic English Sentence"}));
        element.data("constraint", criteria_constraint);
        
        element.find(".remove-criterion").click(function(){
            element.trigger("CriteriaRemovedEvent");
        });
        
        // Display the concept in the main area when the user clicks on the description
        element.find(".field-anchor").click(function(){ //TODO rename this class, its old
           element.trigger("ShowConceptEvent"); 
        });
        
        return(element);
    };

    return {Criteria:Criteria};
});

