require.def('design/views', ['design/chart','design/form'], function(chart,form) {
    
    /**
      Sets up and manages the view sets for each criterion option.
  
      On each request for a criterion option, the response returns an array
      of hashes that contain the information necessary to construct the
      content of the view. For common cases such as simple HTML injection
      or Chart display, the plugin developer does not need to provide
      any special logic for handling those type of views. Custom views
      must be handled using view-specific JS or the view-set JS.
  
      @class
      @author <a href="mailto:millerjm1@email.chop.edu">Jeff Miller</a>
  
      @param {jQuery} $container Represents the containing element which
      encapulates all loaded views
      @param {jQuery} $titleBar Represents the title bar to which the title of
      the Criterion can be set
      @param {jQuery} $tabsBar Represents the element that contains the tabs
      associated with all currently loaded views
      @param {jQuery} $contentBox Represents the content area within the
      container that the active view is displayed
    */
    var manager = function($container, $titleBar, $tabsBar, $contentBox, $addQueryBox) {
        
        var binaryFieldRe = /^(\d*)_(\d*)_input([01])$/;
        var fieldRe = /^(\d*)_(\d*)$/;
        var opRe = /^(\d*)_(\d*)_operator$/;
        
        /**
          A hash with respect to criterion IDs of the objects fetched from
          the server to build the views.
      
          @private
          @type object
        */
        var cache = {};
        
        /**
          The standard template for the tab DOM elements
      
          @private
          @type string
        */
        var tab_tmpl = '<a class="tab" href="#"><%= this.tabname %></a> ';
        /**
          The standard template for the "Add To Query Button"
      
          @private
          @type string
        */
        var add_query_tmpl = '<input id="add_to_query" type="button" value="Add To Query"/>';
        /**
          Holds the currently viewable/active concept/criterionconcept    
      
          @private
          @type int
        */
        var activeConcept = null;

        /**
          Holds the currently viewable view of the currently active 
          concept/criterionconcept
      
          @private
          @type object
        */
        var activeView = null;
 
        /**
          Certain types of concept are built-into the framework.

          We do not have to make external calls to retrieve their code. 
          Control will be passed to the built-in concept code from
          this function
      
          @private 
        */
        function builtinViewCreator(view) {        
            var result = $('<div class="view"></div>')
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
            
            // Give the view its datasource
            result.children().trigger('UpdateDSEvent', [cache[activeConcept].ds]);
            // Show the view
            $container.trigger('ViewReadyEvent', [result]);
        };
    
        /**
          The handler for the 'ViewReadyEvent' event
      
          This event is fired by a concept plugin when it is ready 
          to be inserted into the DOM. $concept here should be a 
          jQuery wrapped set, ready to be placed into the DOM
      
          @private
        */
        function viewReadyHandler(evt, $view) {
            activeView.contents = $view;
            // As of right now IE 7 and 8 cannot seem to properly handle
            // creating VML rotated text in an object that is not in the DOM
            // In those conditions, the chart plugin inserts the graph into the
            // DOM and sets display to 0. We detect here if the element we were
            // passed is in the DOM or not, if not we inject it. The idea is to eventually
            // when we can do this outside the dom in all browsers, to be able to do 
            // this in the existing framework
            if ($view.parent().length === 0){
                // This is not yet in the DOM
                $contentBox.append($view);
            }
            activeView.contents.css("display","block");
            $(".chart", activeView.contents).css("display","block"); // Hack because of IE
            $view.children().trigger("GainedFocusEvent");
            activeView.loaded = true;
        };
    

        /** 
          The handler for the 'ShowViewEvent' event
      
          This event is fired by the tab bar when a new view
          is to be displayed. tabIndex correlates to the view in the 
          activeConcept's views array that needs to be shown.
      
          @private
        */
        function showViewHandler(evt, tabIndex) {
            if (activeView !== null){
                activeView.contents.css("display","none");
                activeView.contents.children().trigger("LostFocusEvent");
                // TODO: Use Modernizer here?
                if ($("shape",activeView.contents).length === 0) {
                    // SVG not VML
                    activeView.contents.detach();
                }
            }
            
            activeView = cache[activeConcept].views[tabIndex];
        
            if (activeView.loaded) {
                viewReadyHandler(null, activeView.contents);
            } else {
                // We have to look at the type of view here, custom views are responsible
                // for triggering the viewReadyHandler once their code is executed,
                // built-in views (which should not have css or js defined on their views, but
                // we will allow it for consistency) will need to be taken care of code here
                var callback = null;
                activeView.concept_id = activeConcept;
                if (activeView.type !== 'custom')
                    callback = builtinViewCreator;
                loadDependencies(activeView, callback);
            }
        };    

        /**
          The handler for the 'UpdateQueryEvent' event
      
          This is fired by a concept when the user clicks
          the concepts 'add to query/update query' button
          This will send off the grammar to the back-end to be
          evaluated and then added to the user's query elements
      
          @private
        */
        function updateQueryHandler(evt, query) {
            console.log(query);
            var concept = cache[activeConcept]
        };

        /**
          The handler for the 'ViewErrorEvent' event
      
          This event is fired by a concept/concept plugin when
          an unrecoveralble error has been received. The framework
          can choose to show the 'Report Error' Panel
      
          @private
        */    

        function viewErrorHandler(evt, details) {

        };
        
        
        /**
            The handler for the 'ElementChangedEvent' event
        
            This event is used by concepts to notify that the user
            has changed the value of an input
        
            @private
       */
        
        function elementChangedHandler(evt, element){
            // Update the concept datastore
            var ds = cache[activeConcept].ds;
            // Did anything actually change?
            // if (ds[element.name] === element.value) return;
            
            // Update teh datasource
            cache[activeConcept].ds[element.name] = element.value;
            // If other views on this concept are already instantiated
            // notify them of the change
            $.each(cache[activeConcept].views, function(index,view) {
                if (activeView !== view && view.contents) {
                    view.contents.children().trigger("UpdateElementEvent",[element]);
                }
            });
        };
        
        /**
              This function is triggered by the "Add To Query" Button,
              for concepts made of builtin views, the function will be responsible
              for analyzing the current concept's datasource and creating the 
              datastructure reprsenting the proper query for the server to 
              perform.
        
              @private
         */
        
        function createAndSendQueryDataStructure(event) {
            // Get the current concept datasource
            var ds = cache[activeConcept].ds;
            var fields={};
            // We need to analyze the current concept and the datasource and construct
            // the proper datastructure to represent this query on the server
            // Find all the different fields and their values in this concept
            for (var item in ds){
                if (!ds.hasOwnProperty(item)) continue;
                var m = fieldRe.exec(item); // Either a choice, assertion, or boolean
                if (m){
                    fields[m[2]] = { val0:ds[item], val1:null, op:null};
                    continue;
                }
                m = binaryFieldRe.exec(item); // decimal
                if (m) {
                    if (fields.hasOwnProperty(m[2])) {
                        fields[m[2]]['val'+m[3]] = ds[item];
                    }else{
                        fields[m[2]] = {val0:null, val1:null, op:null};
                        fields[m[2]]['val'+m[3]] = ds[item];
                    }
                }
            }
            for (item in ds){
                 if (!ds.hasOwnProperty(item)) continue;
                 m = opRe.exec(item);
                 if (m){
                     fields[m[2]]['op'] = ds[item];
                 }
            }
            // We now have the ds sorted into a sensible datastructure
            // based on the fields in the concept. Construct the server
            // required datastructure
            var nodes = [];
            
            for (var field_id in fields) {
                var field = fields[field_id];
                if (field.val0 && field.val1 && field.op) { // Decimal Binary Op
                    nodes.push({
                                    'type' : 'field',
                                    'operator' : field.op,
                                    'id' : field_id,
                                    'value' : [field.val0,field.val1]
                                });
                } else if (field.val0 && field.op && !(field.val0 instanceof Array)){ // Decimal
                    nodes.push({
                                    'type' : 'field',
                                    'operator' : field.op,
                                    'id' : field_id,
                                    'value' : field.val0
                                });
                } else if (field.val0 && field.val0 instanceof Array){ // Choice Same as obove ...
                    // if field.op is null, assume the query was the default, which is "in"
                    field.op = field.op !== null ? field.op : "in";
                    nodes.push({
                                    'type' : 'field',
                                    'operator' : field.op,
                                    'id' : field_id,
                                    'value' : field.val0
                                });
                } else if (field.val0 !== null && !(field.val0 instanceof Array) &&
                           field.op === null && field.val1 === null){ // assertion/or boolean
                     nodes.push({
                                        'type' : 'field',
                                        'operator' : "exact",
                                        'id' : field_id,
                                        'value' : field.val0
                                });
                } else {
                    // Unable to determine what this field is ?
                    throw "Unable to determine field " + field + " in concept " + cache[activeConcept];
                }
            }
            
            var server_query;
            if (nodes.length === 1){
                server_query = nodes;
            }else{
                server_query = [{
                                     'type': 'logic',
                                     'operator': 'and',
                                     'children': nodes
                               }];
            }
            $(event.target).trigger("UpdateQueryEvent", [server_query]); 
        }
        
        
        $container.bind({
            'ViewReadyEvent': viewReadyHandler,
            'UpdateQueryEvent': updateQueryHandler,
            'ViewErrorEvent': viewErrorHandler,
            'ShowViewEvent': showViewHandler,
            'ElementChangedEvent' : elementChangedHandler,
            'UpdateQueryButtonClicked' : createAndSendQueryDataStructure
        });
     
        /**
          A callback does not have to be specified if the view is custom because
          the view code is responsible for firing the ViewReadyEvent
      
          @private
        */
        function loadDependencies(deps, cb) {
            cb = cb || function(){};
        
            if (deps.css)
                LazyLoad.css(deps.css);

            if (deps.js) {
                 LazyLoad.js(deps.js, function () {
                     cb(deps);
                 });
            } else {
                cb(deps);
            }
        };
    
        function loadConcept(concept){
            // If we got here, the globals for the current concept have been loaded
            // We will register it in our cache
            register(concept);
            activeConcept = concept.pk;
            // Mark this concept as having its global dependencies loaded
            concept.globalsLoaded = true; 
            // Setup tabs objects and trigger viewing of the first one
            if (concept.views.length < 2) {
                $tabsBar.css('display','none');
                $container.find('.content').removeClass('content').attr('id','removedContent');
            } else {
                $tabsBar.css('display','block');
                $container.find('#removedContent').addClass('content');
            }
        
            var tabs = $.jqote(tab_tmpl, concept.views);
            $tabsBar.html(tabs); 
            // Regardless of whether the tabs are visible, load the first view
            $tabsBar.children(':first').click();
            
            // If all of the views are builtin, we are going to let the framework
            // handle the add to query button, otherwise the plugin needs to do it
            // (The plugin would raise the UpdateQueryEvent itself)
            var builtin = true;
            $.each(concept.views, function(index, element){
                if (element.type !== "builtin"){
                    builtin = false;
                }
            });
            
            if (builtin){
                $addQueryBox.show();
            }else{
                $addQueryBox.hide();
            }
        };
    
        /**
          Set up the tabs bar for the plugin, we are using the live events to automatically
          create tabs for any <a> elements put into the target area.
          Clicking a tab, will fire a ConceptTabClickEvent, which will be caught by 
          tabClickedHandler. This will fire a 'ShowViewEvent' up the DOM to our listener
      
          @private
        */
        function tabClickedHandler(evt, tab){
            var index = $tabsBar.children().index(tab);
            $tabsBar.trigger('ShowViewEvent', index);
        };

        $tabsBar.bind('ConceptTabClickedEvent', tabClickedHandler);

        $tabsBar.tabs(true, function(evt, $tab) {
            $tab.trigger('ConceptTabClickedEvent',$tab);
        });
        
        
        
        // Prepare the static concept box
        $addQueryBox.hide();
        var $addQueryButton = $('<input id="add_to_query" type="button" value="Add To Query"/>');
        $addQueryButton.click(function(){
             var event = $.Event("UpdateQueryButtonClicked");
             event.target = this;
             $(this).trigger(event); // TODO send current Concept Here to verify its correct
        });
        $addQueryBox.append($addQueryButton);
        
        // PUBLIC METHODS
   
        /**
          Registers a concept
          @public
        */
        function register(concept) {
            if (cache[concept.pk] === undefined)
                cache[concept.pk] = concept;
                // Create a datasource for this concept if we don't have one
                if (!concept.ds){
                    concept.ds = {};
                }
        };

        /**
          Loads and makes a particular concept active and in view
          @public
        */
        function show(concept, index, target) {
           // Verify that we need to do anything.
           if (concept.pk === activeConcept)
               return;

           // Set the name of the concept in the title bar
           $titleBar.text(concept.name);
           if (cache[concept.pk] && cache[concept.pk].globalsLoaded){
                loadConcept(concept);
           } else {
                loadDependencies(concept, loadConcept);
           }
       };
        
       return {
            register: register,
            show: show
        };
    };
    
    return {
        manager: manager
    };
});
