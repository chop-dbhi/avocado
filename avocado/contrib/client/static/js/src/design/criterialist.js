require.def('design/criterialist', ['design/criteria', "design/templates"], function(criteria, templates) {
    
    
    var manager = function($panel){
        var that = {};
        var criteria_cache = {};
        
        // Create the run query buttong
        var $run_query = $(templates.run_query);
        // run the query
        $run_query.click(function(){
            var all_constraints = [];
            for (var key in criteria_cache){
                 if (criteria_cache.hasOwnProperty(key)){
                   all_constraints.push(criteria_cache[key].data("constraint"));
                 }
            }
            console.log(all_constraints);
        });
        
        // Grab the contents of panel now when it is empty
        var $no_criteria_defined = $panel.find("#criteria-list").children();
        
        // Hook into the remove all criteria link
        $panel.find("#remove-criteria").click(function(){
           for (var key in criteria_cache){
               if (criteria_cache.hasOwnProperty(key)){
                   criteria_cache[key].trigger("CriteriaRemovedEvent");
               }
           } 
        });
        
        $panel.bind("UpdateQueryEvent", function(evt, criteria_constraint){
            
            var pk = criteria_constraint[0].concept_id;
            var new_criteria;
            // If this is the first criteria to be added remove 
            // content indicating no criteria is defined, and add 
            // "run query button"
            if ($.isEmptyObject(criteria_cache)){
                $no_criteria_defined.detach();
                $panel.find(".content").append($run_query);
            }
            
            // Is this an update?
            if (criteria_cache.hasOwnProperty(pk)){
                new_criteria = criteria.Criteria(criteria_constraint);
                criteria_cache[pk].replaceWith(new_criteria);
            }else{
                new_criteria = criteria.Criteria(criteria_constraint);
                $panel.find("#criteria-list").append(new_criteria);
            }
            criteria_cache[pk] =  new_criteria;
        });
        
        $panel.bind("CriteriaRemovedEvent", function(evt){
            var $target = $(evt.target);
            var constraint = $target.data("constraint");
            criteria_cache[constraint[0].concept_id].remove();
            delete criteria_cache[constraint[0].concept_id];
            if ($.isEmptyObject(criteria_cache)){
                $panel.find("#criteria-list").append($no_criteria_defined);
                $run_query.detach();
            }
        });
        
        return that;
    };
    return {Manager:manager};
});