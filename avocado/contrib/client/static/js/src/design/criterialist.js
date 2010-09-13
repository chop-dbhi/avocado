require.def('design/criterialist', ['design/criteria', "design/templates"], function(criteria, templates) {
    
    
    var manager = function($panel){
        
        var criteria_cache = {};
        
        var $criteria_div = $panel.find("#criteria-list"),
            $run_query_div = $panel.find(".content"),
            $remove_criteria = $panel.find("#remove-criteria");
            
        
        // Grab the contents of panel while it is empty and save off the 
        // "No Criteria" indicator text
        var $no_criteria_defined = $criteria_div.children();
        
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
        
        // Hook into the remove all criteria link
        $remove_criteria.click(function(){
           for (var key in criteria_cache){
               if (criteria_cache.hasOwnProperty(key)){
                   criteria_cache[key].trigger("CriteriaRemovedEvent");
               }
           } 
        });
        
        // Listen for new criteria as it is added
        $panel.bind("UpdateQueryEvent", function(evt, criteria_constraint){
            
            var pk = criteria_constraint.concept_id;
            var new_criteria;
            // If this is the first criteria to be added remove 
            // content indicating no criteria is defined, and add 
            // "run query button"
            if ($.isEmptyObject(criteria_cache)){
                $no_criteria_defined.detach();
                $run_query_div.append($run_query);
            }
            
            // Is this an update?
            if (criteria_cache.hasOwnProperty(pk)){
                new_criteria = criteria.Criteria(criteria_constraint);
                criteria_cache[pk].replaceWith(new_criteria);
            }else{
                new_criteria = criteria.Criteria(criteria_constraint);
                $criteria_div.append(new_criteria);
            }
            criteria_cache[pk] =  new_criteria;
        });
        
        
        // Listen for removed criteria
        $panel.bind("CriteriaRemovedEvent", function(evt){
            var $target = $(evt.target);
            var constraint = $target.data("constraint");
            criteria_cache[constraint.concept_id].remove();
            delete criteria_cache[constraint.concept_id];
            
            // If this is the last criteria, remove "run query" button
            // and add back "No Criteria" indicator
            if ($.isEmptyObject(criteria_cache)){
                $criteria_div.append($no_criteria_defined);
                $run_query.detach();
            }
        });
        
        var that = {};
        
        
        return that;
    };
    return {Manager:manager};
});