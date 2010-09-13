require.def('design/criterialist', ['design/criteria'], function(criteria) {
    
    
    var manager = function($panel){
        var that = {};
        var criteria_cache = {};
        // Grab the contents of panel now when it is empty
        var $no_criteria_defined = $panel.children();
        $panel.bind("UpdateQueryEvent", function(evt, criteria_constraint){
            
            // Is this an update?
            var new_criteria;
            // If this is the first criteria to be added remove 
            // content indicating no criteria is defined.
            if ($.isEmptyObject(criteria_cache)){
                $no_criteria_defined.detach();
            }
            
            var pk = criteria_constraint[0].concept_id;
            if (criteria_cache.hasOwnProperty(pk)){
                new_criteria = criteria.Criteria(criteria_constraint);
                criteria_cache[pk].replaceWith(new_criteria);
            }else{
                new_criteria = criteria.Criteria(criteria_constraint);
                $panel.append(new_criteria);
            }
            criteria_cache[pk] =  new_criteria;
        });
        
        $panel.bind("CriteriaRemovedEvent", function(evt){
            var $target = $(evt.target);
            var constraint = $target.data("constraint");
            criteria_cache[constraint[0].concept_id].remove();
            delete criteria_cache[constraint[0].concept_id];
            if ($.isEmptyObject(criteria_cache)){
                $panel.append($no_criteria_defined);
            }
        });
        
        return that;
    };
    return {Manager:manager};
});