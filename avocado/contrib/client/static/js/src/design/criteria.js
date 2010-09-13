require.def('design/criteria', ['design/templates'], function(templates) {
    var tmpl = $.jqotec(templates.scope_element);
    
    var Criteria = function(criteria_constraint){
        console.log(criteria_constraint);
        var element = $($.jqote(tmpl, {pk:criteria_constraint[0].concept_id, description:"Generic English Sentence"}));
        element.data("constraint", criteria_constraint);
        
        element.find(".remove-criterion").click(function(){
            element.trigger("CriteriaRemovedEvent");
        });
        
        return(element);
    };

    return {Criteria:Criteria};
});

