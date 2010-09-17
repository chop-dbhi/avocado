require.def('design/criterialist', ['design/criteria', "design/templates","lib/json2"], function(criteria, templates) {
    
    
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
            var server_query;
            for (var key in criteria_cache){
                 if (criteria_cache.hasOwnProperty(key)){
                   all_constraints.push(criteria_cache[key].data("constraint"));
                 }
            }
            
            
            if (all_constraints.length < 2){
                server_query = all_constraints[0];
            }else{
                server_query = {type: "and", children : all_constraints};
            }
            $.putJSON('/api/scope/session/', JSON.stringify(server_query));
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
        
        var that = {
            fireFirstCriteria: function(){
               if (!$.isEmptyObject(criteria_cache)){
                  $($criteria_div.children()[0]).trigger("ShowConceptEvent");
                }
            },
            retrieveCriteriaDS: function(concept_id) {
                var ds = null;
                concept_id && $.each($criteria_div.children(), function(index,element){
                    if ($(element).data("constraint").concept_id == concept_id){ // TODO cast to string for both
                        ds = $(element).data("constraint");
                    }
                });
                return ds;
            }
            
            
        };
        
        
        return that;
    };
    return {Manager:manager};
});