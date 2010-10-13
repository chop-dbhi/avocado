require(['define/search', 'define/conceptmanager', 'define/criteriamanager'], function(search, conceptmanager, criteriamanager) {
   
    $(function() {
        search.init();
        // The view manager needs to know where in the DOM to place certain things
        var rootNode = $("#content"),
            pluginTabs = $('#plugin-tabs'),
            pluginPanel = $('#plugin-panel'),
            pluginTitle = $('#plugin-title'),
            criteriaPanel = $("#user-criteria"),
            pluginStaticContent = $('#plugin-static-content'),
            pluginDynamicContent = $('#plugin-dynamic-content'),

            criteria = $('#criteria');
            
            
        // Create an instance of the conceptManager object. Only do this once.
        var conceptManager = conceptmanager.manager(pluginPanel, pluginTitle, pluginTabs, pluginDynamicContent,
            pluginStaticContent);
        
        var criteriaManager = criteriamanager.Manager(criteriaPanel);
        
        rootNode.bind('UpdateQueryEvent', function(evt, criteria_constraint) {
            criteriaPanel.triggerHandler("UpdateQueryEvent", [criteria_constraint]);
        });
        
        rootNode.bind("ConceptAddedEvent ConceptDeletedEvent", function(evt){
            pluginPanel.trigger(evt);
        });
        
        // There are currently three ways this event can be triggered.
        // 1) Clicking on concept in the left hand-side menu
        //    a)  Slightly differently, a user can click on a concept in the left
        //        hand panel while that concept is already part of a question in the
        //        right-hand query panel, in which case, the data needs to be retrieved
        //        from the query component. 
        // 2) Clicking on a criteria from the query box on the right-hand side
        // 3) Clicking on a tab where a concept has already been opened while on 
        //    another tab. For example, if you were on Audiology Tab, selected ABR 1000,
        //    and then moved to Imaging, and then clicked back on Audiology.
        rootNode.bind("ShowConceptEvent", function(evt){
            var target = $(evt.target);
            var concept_id = target.attr('data-id');
            var existing_ds = evt.constraints; // if they clicked on the right side
            if (!existing_ds){
                // Criteria manager will have constraints if this is already in the right side
                // but they clicked on the concept in the left side
                existing_ds = criteriaManager.retrieveCriteriaDS(concept_id);
            }

            if (conceptManager.isConceptLoaded(concept_id)){
                pluginPanel.fadeIn(100);
                conceptManager.show({id: concept_id}, existing_ds);
            }else{
                $.ajax({
                    url: target.attr('data-uri'),
                    dataType:'json',
                    success: function(json) {
                            pluginPanel.fadeIn(100);
                            conceptManager.show(json, existing_ds);
                        }
                    });
            }    
        });
        
// TODO change this into a jQuery extension or something..
//        (function() {
//            var cache = {},
//                tools = $('#tools'),
//                tools_width = tools.width(),
//                left_pad = right_pad = 10,
//                ft = 100;
//            
//            function get(e) {
//                if (!cache[e.id]) {
//                    // center the menu unless it conflicts with the far right
//                    // or left edges
//                    var label = $(e),
//                        menu = $(label.attr('data-for')),
//                        menu_width = menu.outerWidth();
//            
//                    // absolute midpoint of label
//                    var label_abs_mid = label.offset().left + (label.outerWidth() / 2),
//                        menu_abs_right = label_abs_mid + (menu_width / 2);
//                    
//                    // menu overflows right edge of document, default to right edge
//                    if (menu_abs_right >= document.width - right_pad) {
//                        menu.css('right', right_pad);
//                    } else {
//                        menu.css('right', document.width - menu_abs_right);
//                    }
//                    cache[e.id] = [label, menu];
//                }
//                return cache[e.id];
//            };
//            
//            function hide() {
//                for (var e in cache) {
//                    cache[e][1].hide();
//                    cache[e][0].removeClass('selected');
//                }
//            };
//
//            tools.delegate('#tools > *', 'click', function(evt) {
//                var e = get(this), t = e[0], m = e[1];
//                
//                if (t.hasClass('selected')) {
//                    m.fadeOut(ft);
//                    t.removeClass('selected');
//                } else {
//                    hide();
//                    t.addClass('selected');
//                    m.fadeIn(ft);
//                }
//            });            
//        })();
//
//

        rootNode.bind('activate-criterion', function(evt, id) {
            var target;

            if (!id)
                target = $(evt.target);
            else
                target = criteria.children('[data-id=' + id + ']');

            id = id || target.attr('data-id');

            // remove active state for all siblings
            target.addClass('active').siblings().removeClass('active');

            target.trigger('ShowConceptEvent');
            // bind this concept's id to the current active tab
            rootNode.trigger('setid-tab', [id]);

            return false;
        });
 
        $('[data-model=criterion]').live('click', function(evt) {
            $(this).trigger('activate-criterion');
            return false;
        });
    });
});
