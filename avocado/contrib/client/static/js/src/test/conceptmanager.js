require.def('test/conceptmanager',
            ['define/conceptmanager'],
            function(manager) {
                
    Object.prototype.equals = function(x)
    {
        for(p in this)
        {
            if(typeof(x[p])=='undefined') {return false;}
        }
        
        for(p in this)
        {
            if (this[p])
            {
                var objectType = typeof(this[p]);
                if ((objectType === "object")  && (this[p].constructor === Array)){
                    objectType = 'array';
                }
                
                switch(objectType)
                {       case 'array' :
                                var otherObjectType = typeof(x[p]);
                                if (!((otherObjectType === "object") && (x[p].constructor === Array))){
                                   // not an array
                                   return false;
                                }
                                if (this[p].length !== x[p].length){
                                    return false;
                                }
 
                                for (var i = 0; i < this[p].length; i++){
                                    var found = false;
                                    for (var j = 0; j < x[p].length; j++){
                                        if (this[p][i].equals(x[p][j])) found = true;
                                    }
                                    if (!found){
                                        return false;
                                    }
                                }
                                break;
                        case 'object':
                                if (!this[p].equals(x[p])) { return false; } break;
                        case 'function':break;
                               // if (typeof(x[p])=='undefined' || (p != 'equals' && this[p].toString() != x[p].toString())) { return false; }; break;
                        default:
                                if (this[p] != x[p]) { return false; }
                }
            }
            else
            {
                if (x[p])
                {
                    return false;
                }
            }
        }
        
        for(p in x)
        {
            if(typeof(this[p])=='undefined') {return false;}
        }
        
        return true;
    };

   var $arena = $(['<div id="plugin-panel" class="container">',
   '<div id="plugin-tabs" class="toolbar header tabs hidden"></div>',
   '<div class="content">',
   '<div id="plugin-dynamic-content"></div>',
   '<div id="plugin-static-content"></div>',
   '</div>',
   '</div>'].join(""));
   
   var $dom_dummy = $("<div></div>");
   
   var api = { concept:"/api/criteria" };
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
       },
       93: { 
           "name": "Patient has ABR", 
           "js": null, 
           "id": 93, 
           "css": null, 
           "views": [
               {
                   "elements": [
                       {
                           "type": "chart", 
                           "data": {
                               "name": "Has at least one ABR", 
                               "title": "Patients Having an ABR", 
                               "datatype": "boolean", 
                               "yaxis": "", 
                               "choices": [
                                   [
                                       true, 
                                       "Yes"
                                   ], 
                                   [
                                       false, 
                                       "No"
                                   ]
                               ], 
                               "coords": [
                                   [
                                       true, 
                                       300
                                   ], 
                                   [
                                       false, 
                                       50000
                                   ]
                               ], 
                               "xaxis": "", 
                               "pk": 170, 
                               "optional": false
                           }
                       }
                   ], 
                   "type": "builtin", 
                   "tabname": "Default View"
               }
           ]
       }
   };
   
   $('#arena').append($arena);

   var $pluginPanel = $('#plugin-panel'),
       $pluginTabs = $('#plugin-tabs'),
       $pluginTitle = $('#plugin-title'),
       $pluginStaticContent = $('#plugin-static-content'),
       $pluginDynamicContent = $('#plugin-dynamic-content');

   var ConceptManager = manager.manager($pluginPanel,
                                        $pluginTitle,
                                        $pluginTabs,
                                        $pluginDynamicContent,
                                        $pluginStaticContent);
   
   var event = {
         target: $dom_dummy
   };           
   module("Concept Manager");
   test('ConceptManager Datasource Error Checking.', 7, function() {
      ConceptManager.show(criteria[11]);
      $dom_dummy.bind("InvalidInputEvent", function(evt){
            ok(true, "Empty datasource raises error");
            $dom_dummy.unbind(); 
      });
      ConceptManager.constructQueryHandler(event, {});
      $dom_dummy.bind("InvalidInputEvent", function(evt){
              ok(true, "Datasource with empty list raises error.");
              $dom_dummy.unbind(); 
      });
      ConceptManager.constructQueryHandler(event, {"32_32":undefined});
      $dom_dummy.bind("InvalidInputEvent", function(evt){
              ok(true, "Datasource with undefined raises error.");
              $dom_dummy.unbind(); 
      });
      
      ConceptManager.constructQueryHandler(event, {"32_32":''});
      $dom_dummy.bind("InvalidInputEvent", function(evt){
              ok(true, "Datasource with empty string raises error.");
              $dom_dummy.unbind(); 
      });
      ConceptManager.constructQueryHandler(event, {"32_32":null});
      $dom_dummy.bind("InvalidInputEvent", function(evt){
              ok(true, "Datasource with null value raises error.");
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
   
   
   // This test is will send a series of datasources into the
   // query construction code and verify that the correct query 
   // is created
   
   var ds = {};
   var query = null;
   var key = null;
   
   test('ConceptManager Query Construction.', 1, function() {
        ConceptManager.show(criteria[93]);
        key = {
            concept_id: 93,
            datatype: "boolean",
            id: 170,
            operator: "exact",
            value: false
        };
        
        ds={'93_170':[false]};
        query = ConceptManager.buildQuery(ds);
        ok(ConceptManager.buildQuery(ds).equals(key), "Query for a boolean search field is correct");
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
