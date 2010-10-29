require.def('test/conceptmanager',
            ['define/conceptmanager'],
            function(manager) {
   var $arena = $(['<div id="plugin-panel" class="container">',
   '<div id="plugin-tabs" class="toolbar header tabs hidden"></div>',
   '<div class="content">',
   '<div id="plugin-dynamic-content"></div>',
   '<div id="plugin-static-content"></div>',
   '</div>',
   '</div>'].join());
   
   var $dom_dummy = $("<div></div>");
   
   var api = { concept:"/api/criteria"};
   var criteria = {  
       11 : {
           "name": "500 Hz Response", 
           "js": null, 
           "id": 11, 
           "css": null, 
           "views": [
               {
                   "elements": [
                       {
                           "type": "chart", 
                           "data": {
                               "name": "500 Hz Response", 
                               "title": "Distribution of 500 Hz Audiogram Response", 
                               "datatype": "number", 
                               "yaxis": "# of Responses", 
                               "choices": null, 
                               "coords": [
                                   [
                                       32, 
                                       5
                                   ], 
                                   [
                                       93, 
                                       43
                                   ]
                               ], 
                               "xaxis": "Response (dB)", 
                               "pk": 124, 
                               "optional": false
                           }
                       }, 
                       {
                           "fields": [
                               {
                                   "datatype": "string", 
                                   "pk": 125, 
                                   "optional": true, 
                                   "name": "Test Conditions", 
                                   "choices": [
                                       [
                                           "M", 
                                           "M"
                                       ], 
                                       [
                                           "MN", 
                                           "MN"
                                       ], 
                                       [
                                           "MV", 
                                           "MV"
                                       ], 
                                       [
                                           "N", 
                                           "N"
                                       ], 
                                       [
                                           "V", 
                                           "V"
                                       ], 
                                       [
                                           null, 
                                           "No Data"
                                       ]
                                   ]
                               }
                           ], 
                           "type": "form"
                       }
                   ], 
                   "type": "builtin", 
                   "tabname": "Default View"
               }
           ]
       }
   }

   var $pluginPanel = $('#plugin-panel', $arena),
       $pluginTabs = $('#plugin-tabs', $arena),
       $pluginTitle = $('#plugin-title', $arena),
       $pluginStaticContent = $('#plugin-static-content', $arena),
       $pluginDynamicContent = $('#plugin-dynamic-content', $arena);

   var ConceptManager = manager.manager($pluginPanel,
                                        $pluginTitle,
                                        $pluginTabs,
                                        $pluginDynamicContent,
                                        $pluginStaticContent);
                                        
   module("Concept Manager");
   test('ConceptManager Error Checking.', 4, function() {
      var event = {
          target: $dom_dummy
      };
      $dom_dummy.bind("InvalidInputEvent", function(evt){
            ok(true, "Empty datasource raises error");
            $dom_dummy.unbind(); 
      });
      ConceptManager.constructQueryHandler(event, {});
      $dom_dummy.bind("InvalidInputEvent", function(evt){
              ok(true, "Datasource with empty list raises error.");
              $dom_dummy.unbind(); 
      });
      ConceptManager.constructQueryHandler(event, {"32_32":[]});
      $dom_dummy.bind("InvalidInputEvent", function(evt){
                ok(true, "Datasource with only operators raises error");
                $dom_dummy.unbind(); 
      });
      ConceptManager.constructQueryHandler(event, {"32_32_operator":"exact"});
      ok(ConceptManager.constructQueryHandler(event, {"32_32_operator":"isnull"}),
         "Datasource with operator isnull does not raise error");
      
   });
   
   // There is some odd behavior here when use requireJS with QUnit.
   // QUnit uses a Window Load event to fire the code that calls
   // QUnit.start(). Under more normal circumstances, by time
   // the event fires all of the test modules have run and been
   // added to QUnit.config.queue, so when QUnit.start() is called
   // all those test run. But when we use requireJS, the test
   // code does not run until after, and therefore the queue is empty
   // when QUnit.start is first called, so we call it here manually.
   QUnit.start();
});
