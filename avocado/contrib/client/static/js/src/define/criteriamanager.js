require.def('define/criteriamanager', ['define/criteria', "define/templates","lib/json2"], function(criteria, templates) {
    
    var manager = function($panel){
        
        var criteria_cache = {};
        
        var $criteria_div = $panel.find("#criteria-list"),
            $run_query_div = $panel.find(".content"),
            $remove_criteria = $panel.find("#remove-criteria");
        
        var criteria_api_uri = $criteria_div.attr("data-uri");
        var report_url = $criteria_div.attr("data-report");
        var session_api_uri = $panel.attr("data-uri");
        
        
        // Grab the contents of panel while it is empty and save off the 
        // "No Criteria" indicator text
        var $no_criteria_defined = $criteria_div.children();
        
        // Create the run query button
        var $run_query = $(templates.run_query);
        
        // Load any criteria on the session
        $.getJSON(session_api_uri, function(data){
              if ((data.store === null) || $.isEmptyObject(data.store)){
                  return;
              }
              
              if (!data.store.hasOwnProperty("concept_id")){ // Root node representing a list of concepts won't have this attribute
                  $.each(data.store.children, function(index, criteria_constraint){
                      $panel.triggerHandler("UpdateQueryEvent", [criteria_constraint]);
                  });
              }else{
                  $panel.triggerHandler("UpdateQueryEvent", [data.store]);
              }

             // If we have any criteria, show the first one.
             if (!$.isEmptyObject(criteria_cache)){
                $($criteria_div.children()[0]).find(".field-anchor").click();
             }
        });

        // Setup click even handlers
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
            $.putJSON(session_api_uri, JSON.stringify(server_query), function(){
                window.location=report_url;
            });
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
            }else{
                $criteria_div.children(".criterion").removeClass("selected");
            }
            
            // Is this an update?
            if (criteria_cache.hasOwnProperty(pk)){
                new_criteria = criteria.Criteria(criteria_constraint, criteria_api_uri);
                criteria_cache[pk].replaceWith(new_criteria);
                new_criteria.fadeTo(300, 0.5, function() {
                      new_criteria.fadeTo("fast", 1);
                });
            }else{
                new_criteria = criteria.Criteria(criteria_constraint, criteria_api_uri);
                $criteria_div.append(new_criteria);
                var addEvent = $.Event("ConceptAddedEvent");
                addEvent.concept_id = pk;
                $panel.trigger(addEvent);
            }
            criteria_cache[pk] =  new_criteria;
        });


        // Listen for removed criteria
        $panel.bind("CriteriaRemovedEvent", function(evt){
            var $target = $(evt.target);
            var constraint = $target.data("constraint");
            criteria_cache[constraint.concept_id].remove();
            delete criteria_cache[constraint.concept_id];
            
            var removedEvent = $.Event("ConceptDeletedEvent");
            removedEvent.concept_id = constraint.concept_id;
            $panel.trigger(removedEvent);
            
            // If this is the last criteria, remove "run query" button
            // and add back "No Criteria" indicator
            if ($.isEmptyObject(criteria_cache)){
                $criteria_div.append($no_criteria_defined);
                $run_query.detach();
            }
        });
        
        // Listen to see if the user clicks on any of the criteria.
        // Highlight the selected criteria to make it clear which one is
        // displayed
        $panel.bind("ShowConceptEvent", function (evt){
              var $target = $(evt.target);
              $criteria_div.children(".criterion").removeClass("selected");
              if  ($target.is(".criterion")){
                  $target.addClass("selected");
              }else{
                  // If the user clicked on the left-hand side, but we have this criteria
                  // defined, highlight it.
                  var id = evt.originalEvent.concept_id;
                  criteria_cache[id] && criteria_cache[id].addClass("selected");
              }
        });

        var that = {
            retrieveCriteriaDS: function(concept_id) {
                var ds = null;
                concept_id && $.each($criteria_div.children(), function(index,element){
                    if (!$(element).data("constraint")){
                        return; // could just be text nodes
                    }
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