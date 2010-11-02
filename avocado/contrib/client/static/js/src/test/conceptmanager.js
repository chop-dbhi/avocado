require.def('test/conceptmanager',
            ['define/conceptmanager'],
            function(manager) {
                
    var equivalent = function(x,y)
    {   var p = null;
        for(p in y)
        {
            if(typeof(x[p])=='undefined') {return false;}
        }
        
        for(p in y)
        {
            if (y[p])
            {
                var objectType = typeof(y[p]);
                if ((objectType === "object")  && (y[p].constructor === Array)){
                    objectType = 'array';
                }
                
                switch(objectType)
                {       case 'array':
                                var otherObjectType = typeof(x[p]);
                                if (!((otherObjectType === "object") && (x[p].constructor === Array))){
                                   // not an array
                                   return false;
                                }
                                if (x[p] === undefined || y[p].length !== x[p].length){
                                    return false;
                                }
 
                                for (var i = 0; i < y[p].length; i++){
                                    var found = false;
                                    for (var j = 0; j < x[p].length; j++){
                                        if (equivalent(y[p][i],x[p][j])) found = true;
                                    }
                                    if (!found){
                                        return false;
                                    }
                                }
                                break;
                        case 'object':
                                if (!equivalent(y[p],x[p])) { return false; } break;
                        case 'function':break;
                               // if (typeof(x[p])=='undefined' || (p != 'equals' && y[p].toString() != x[p].toString())) { return false; }; break;
                        default:
                                if (y[p] != x[p]) { return false; }
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
            if(typeof(y[p])=='undefined') {return false;}
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
       },
       43: {
           "name": "Audiometry Test Condition", 
           "js": null, 
           "id": 43, 
           "css": null, 
           "views": [
               {
                   "elements": [
                       {
                           "type": "chart", 
                           "data": {
                               "name": "Audiometry Test Condition", 
                               "title": "Audiometry Test Condition", 
                               "datatype": "string", 
                               "yaxis": "# of Tests", 
                               "choices": [
                                   [
                                       "Aided", 
                                       "Aided"
                                   ], 
                                   [
                                       "Air", 
                                       "Air"
                                   ], 
                                   [
                                       "Bone", 
                                       "Bone"
                                   ], 
                                   [
                                       "Cochlear Implant", 
                                       "Cochlear Implant"
                                   ], 
                                   [
                                       "Noise", 
                                       "Noise"
                                   ], 
                                   [
                                       "Sound Field", 
                                       "Sound Field"
                                   ], 
                                   [
                                       "Warble", 
                                       "Warble"
                                   ]
                               ], 
                               "coords": [
                                   [
                                       "Aided", 
                                       70
                                   ], 
                                   [
                                       "Air", 
                                       73032
                                   ], 
                                   [
                                       "Bone", 
                                       53232
                                   ], 
                                   [
                                       "Cochlear Implant", 
                                       13234
                                   ], 
                                   [
                                       "Noise", 
                                       23343
                                   ], 
                                   [
                                       "Sound Field", 
                                       234
                                   ], 
                                   [
                                       "Warble", 
                                       23432
                                   ]
                               ], 
                               "xaxis": "Condition", 
                               "pk": 119, 
                               "optional": false
                           }
                       }
                   ], 
                   "type": "builtin", 
                   "tabname": "Default View"
               }
           ]
       },
       60: {
           "name": "Has Sensorineural Loss?", 
           "js": null, 
           "id": 60, 
           "css": null, 
           "views": [
               {
                   "elements": [
                       {
                           "type": "chart", 
                           "data": {
                               "name": "Has Sensorineural Loss?", 
                               "title": "Has Sensorineural Loss?", 
                               "datatype": "nullboolean", 
                               "yaxis": null, 
                               "choices": [
                                   [
                                       true, 
                                       "Yes"
                                   ], 
                                   [
                                       false, 
                                       "No"
                                   ], 
                                   [
                                       null, 
                                       "No Data"
                                   ]
                               ], 
                               "coords": [
                                   [
                                       false, 
                                       5000
                                   ], 
                                   [
                                       true, 
                                       6000
                                   ], 
                                   [
                                       null, 
                                       10000
                                   ]
                               ], 
                               "xaxis": null, 
                               "pk": 116, 
                               "optional": false
                           }
                       }
                   ], 
                   "type": "builtin", 
                   "tabname": "Default View"
               }
           ]
       },
       50: {
           "name": "Ear Canal Volume (ECV)", 
           "js": null, 
           "id": 50, 
           "css": null, 
           "views": [
               {
                   "elements": [
                       {
                           "type": "chart", 
                           "data": {
                               "name": "Ear Canal Volume (ECV)", 
                               "title": "Distribution of Ear Canal Volume (ECV)", 
                               "datatype": "number", 
                               "yaxis": "# of Tests", 
                               "choices": null, 
                               "coords": [
                                   [
                                       2.7, 
                                       1
                                   ], 
                                   [
                                       4.2, 
                                       1
                                   ]
                               ], 
                               "xaxis": "Volume (mL)", 
                               "pk": 157, 
                               "optional": false
                           }
                       }
                   ], 
                   "type": "builtin", 
                   "tabname": "Default View"
               }
           ]
       },
       1: {
           "name": "Pure Tone Average (PTA)", 
           "js": null, 
           "id": 1, 
           "css": null, 
           "views": [
               {
                   "elements": [
                       {
                           "type": "chart", 
                           "data": {
                               "pkchoice_default": 142, 
                               "name": "Pure Tone Average", 
                               "title": "Distribution of Pure Tone Average", 
                               "pkchoices": [
                                   [
                                       142, 
                                       "either ear"
                                   ], 
                                   [
                                       151, 
                                       "the better ear"
                                   ], 
                                   [
                                       152, 
                                       "the worse ear"
                                   ]
                               ], 
                               "pkchoice_label": "in", 
                               "yaxis": "# Audiogram Results", 
                               "datatype": "number", 
                               "coords": [
                                   [
                                       0.0, 
                                       192
                                   ], 
                                   [
                                       1, 
                                       32
                                   ] 
                                  
                               ], 
                               "xaxis": "PTA (dB)"
                           }
                       }, 
                       {
                           "fields": [
                               {
                                   "datatype": "boolean", 
                                   "pk": 143, 
                                   "default": true, 
                                   "name": "Exclude PTA's with one or more 'no response' values"
                               }
                           ], 
                           "type": "form"
                       }
                   ], 
                   "type": "builtin", 
                   "tabname": "Chart"
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
   module("ConceptManager");
   test('Datasource Error Checking.', 7, function() {
      ConceptManager.show(criteria[11]);
      $dom_dummy.bind("InvalidInputEvent", function(evt){
            ok(true, "Empty datasource raises error");
      });
      ConceptManager.constructQueryHandler(event, {});
      $dom_dummy.unbind(); 
      
      
      $dom_dummy.bind("InvalidInputEvent", function(evt){
              ok(true, "Datasource with empty list raises error.");
      });
      ConceptManager.constructQueryHandler(event, {"32_32":[]});
      $dom_dummy.unbind(); 
      
      $dom_dummy.bind("InvalidInputEvent", function(evt){
              ok(true, "Datasource with undefined raises error.");
      });
      ConceptManager.constructQueryHandler(event, {"32_32":undefined});
      $dom_dummy.unbind(); 
      
      $dom_dummy.bind("InvalidInputEvent", function(evt){
              ok(true, "Datasource with empty string raises error.");
      });
      ConceptManager.constructQueryHandler(event, {"32_32":''});
      $dom_dummy.unbind(); 
      
      ok(ConceptManager.constructQueryHandler(event, {"32_32":null}), "Datasource with null value does not raise error.");
      
      $dom_dummy.bind("InvalidInputEvent", function(evt){
                ok(true, "Datasource with only operators raises error");; 
      });
      ConceptManager.constructQueryHandler(event, {"32_32_operator":"exact"});
      $dom_dummy.unbind(); 
      
      ok(ConceptManager.constructQueryHandler(event, {"32_32_operator":"isnull"}),
         "Datasource with operator isnull does not raise error");
   });
   
   
   // This test is will send a series of datasources into the
   // query construction code and verify that the correct query 
   // is created
   
   var ds = {};
   var query = null;
   var key = null;
   
   test('Boolean Query Construction.', 6, function() {
        ConceptManager.show(criteria[93]);
        key = {
            concept_id: 93,
            datatype: "boolean",
            id: 170,
            operator: "exact",
            value: false
        };
        ds={'93_170':[false]};
        ok(equivalent(ConceptManager.buildQuery(ds),key), "Query for a boolean search field with one selected with no operator specified.");
        
        key = {
            concept_id: 93,
            datatype: "boolean",
            id: 170,
            operator: "exact",
            value: true
        };
        ds={'93_170':[true], '93_170_operator':'in'};
        ok(equivalent(ConceptManager.buildQuery(ds),key), "Query for a boolean search field with one selected with 'in' operator specified.");
        
        key = {
            concept_id: 93,
            datatype: "boolean",
            id: 170,
            operator: "-exact",
            value: true
        };
        ds={'93_170':[true], '93_170_operator':'-in'};
        ok(equivalent(ConceptManager.buildQuery(ds),key), "Query for a boolean search field with one selected with negated operator specified.");

        key = {
            'type': 'or',
            'children': [
                 {
                        concept_id: 93,
                        datatype: "boolean",
                        id: 170,
                        operator: "exact",
                        value: false
                 },
                 {
                     
                        concept_id: 93,
                        datatype: "boolean",
                        id: 170,
                        operator: "exact",
                        value: true
                 }
             
             ],
             'concept_id': 93
        };
        ds={'93_170':[false,true]};
        ok(equivalent(ConceptManager.buildQuery(ds),key), "Query for a boolean search field with both selected with no operator specified.");
        
        ds={'93_170':[false,true], '93_170_operator':'in'};
        ok(equivalent(ConceptManager.buildQuery(ds),key), "Query for a boolean search field with both selected with 'in' operator specified.");
        
        key = {
            'type': 'and',
            'children': [
                 {
                        concept_id: 93,
                        datatype: "boolean",
                        id: 170,
                        operator: "-exact",
                        value: false
                 },
                 {
                     
                        concept_id: 93,
                        datatype: "boolean",
                        id: 170,
                        operator: "-exact",
                        value: true                     
                 }
             
             ],
             'concept_id': 93
        };
        ds={'93_170':[true, false], '93_170_operator':'-in'};
        ok(equivalent(ConceptManager.buildQuery(ds),key), "Query for a boolean search field with both selected with negated operator.");
   });
   
   test('String Choice Query Construction',6 , function(){
        ConceptManager.show(criteria[43]);
        key = {
            concept_id: 43,
            id: 119,
            operator: "in",
            value: [ 
               "Air",
               "Bone",
               "Cochlear Implant",
               "Noise"
            ]
        };
        ds = { 
            "43_119": [
                "Air",
                "Bone",
                "Cochlear Implant",
                "Noise"
            ]
        };
        ok(equivalent(ConceptManager.buildQuery(ds),key), "Query for a string choice field with multiple selected with no operator specified.");
        
        ds = { 
            "43_119": [
                "Air",
                "Bone",
                "Cochlear Implant",
                "Noise"
            ],
            "43_119_operator" : "in"
        };
        ok(equivalent(ConceptManager.buildQuery(ds),key), "Query for a string choice field with multiple selected with 'in' operator specified.");
        
        key = {
            concept_id: 43,
            id: 119,
            operator: "-in",
            value: [ 
               "Air",
               "Bone",
               "Cochlear Implant",
               "Noise"
            ]
        };
        ds = { 
            "43_119": [
                "Air",
                "Bone",
                "Cochlear Implant",
                "Noise"
            ],
            "43_119_operator" : "-in"
        };
        ok(equivalent(ConceptManager.buildQuery(ds),key), "Query for a string choice field with multiple selected with negated operator specified.");
        
        
        key = {
            concept_id: 43,
            id: 119,
            operator: "in",
            value: [ 
               "Air"
            ]
        };
        ds = { 
            "43_119": [
                "Air"
            ]
        };
        ok(equivalent(ConceptManager.buildQuery(ds),key), "Query for a string choice field with one selected with no operator specified.");
        
        ds = { 
            "43_119": [
                "Air"
            ],
            "43_119_operator" : "in"
        };
        ok(equivalent(ConceptManager.buildQuery(ds),key), "Query for a string choice field with one selected with 'in' operator specified.");
        
        key = {
            concept_id: 43,
            id: 119,
            operator: "-in",
            value: [ 
               "Air"
            ]
        };
        ds = { 
            "43_119": [
                "Air"
            ],
            "43_119_operator" : "-in"
        };
        ok(equivalent(ConceptManager.buildQuery(ds),key), "Query for a string choice field with one selected with negated operator specified.");
   });
   
   test("Nullboolean Query Construction",7,function(){
      ConceptManager.show(criteria[60]);
      
      key = { 
          concept_id: 60,
          datatype: "nullboolean",
          id: 116,
          operator: "exact",
          value: null
      };
      ds = {
          "60_116": [
            null
          ]
      };
      ok(equivalent(ConceptManager.buildQuery(ds),key), "Query for nullboolean field with one selected (null value) with no operator specified.");
      
      ds = {
          "60_116": [
            null
          ],
          "60_116_operator" : "in"
      };
      ok(equivalent(ConceptManager.buildQuery(ds),key), "Query for nullboolean field with one selected (null value) with 'in' operator specified.");
      
      key = { 
          concept_id: 60,
          datatype: "nullboolean",
          id: 116,
          operator: "-exact",
          value: null
      };
      ds = {
          "60_116": [
            null
          ],
          "60_116_operator" : "-in"
      };
      ok(equivalent(ConceptManager.buildQuery(ds),key), "Query for nullboolean field with one selected (null value) with negated specified.");
      
      key = {
          children: [
            {
                concept_id: 60,
                datatype: "nullboolean",
                id: 116,
                operator: "exact",
                value: null
            },
            {
                concept_id: 60,
                datatype: "nullboolean",
                id: 116,
                operator: "exact",
                value: false
            }
          ],
          concept_id: 60,
          type: "or"
      };
      ds = {
          '60_116': [
              null,
              false
          ]
      };
      ok(equivalent(ConceptManager.buildQuery(ds),key), "Query for nullboolean field with two selected (null,true ) with no operator specified.");
      
      ds = {
            '60_116': [
                null,
                false
            ],
            "60_116_operator" : "in"
      };
      ok(equivalent(ConceptManager.buildQuery(ds),key), "Query for nullboolean field with two selected (null,true ) with 'in' operator specified.");
      
      key = {
          children: [
            {
                concept_id: 60,
                datatype: "nullboolean",
                id: 116,
                operator: "-exact",
                value: null
            },
            {
                concept_id: 60,
                datatype: "nullboolean",
                id: 116,
                operator: "-exact",
                value: false
            }
          ],
          concept_id: 60,
          type: "and"
      };
      ds = {
          '60_116': [
              null,
              false
          ],
          "60_116_operator" : "-in"
      };
      ok(equivalent(ConceptManager.buildQuery(ds),key), "Query for nullboolean field with two selected (null,true ) with negated operator specified.");
      
      key = {
          children: [
            {
                concept_id: 60,
                datatype: "nullboolean",
                id: 116,
                operator: "-exact",
                value: null
            },
            {
                concept_id: 60,
                datatype: "nullboolean",
                id: 116,
                operator: "-exact",
                value: false
            },
            {
                concept_id: 60,
                datatype: "nullboolean",
                id: 116,
                operator: "-exact",
                value: true
            }
          ],
          concept_id: 60,
          type: "and"
      };
      ds = {
          '60_116': [
              null,
              false,
              true
          ],
          "60_116_operator" : "-in"
      };
      ok(equivalent(ConceptManager.buildQuery(ds),key), "Query for nullboolean field with all selected with negated operator specified.");
   });
   
   test('Number Query Construction',5,function(){
       ConceptManager.show(criteria[50]);
       
       key = {
           concept_id: 50,
           datatype: "number",
           id: 157,
           operator: "range",
           value: [
               3.6,
               5.9
           ]
       };
       ds = {
           '50_157_input0': "3.6",
           '50_157_input1': "5.9",
           '50_157_operator': "range"
       };
       ok(equivalent(ConceptManager.buildQuery(ds),key), "Query for number field with range operator specified.");
       
       key = {
           concept_id: 50,
           datatype: "number",
           id: 157,
           operator: "-range",
           value: [
               3.6,
               5.9
           ]
       };
       ds = {
           '50_157_input0': "3.6",
           '50_157_input1': "5.9",
           '50_157_operator': "-range"
       };
       ok(equivalent(ConceptManager.buildQuery(ds),key), "Query for number field with negated range operator specified.");
       
       key = {
           concept_id: 50,
           datatype: "number",
           id: 157,
           operator: "lte",
           value: 4
       };
       ds={
           '50_157_input0': "4",
           '50_157_operator': "lte"
       };
       ok(equivalent(ConceptManager.buildQuery(ds),key), "Query for number field with lte operator specified.");
        
       key = {
           concept_id: 50,
           datatype: "number",
           id: 157,
           operator: "isnull",
           value: true
       };
       ds = {
           '50_157_operator': "isnull"
       };
       ok(equivalent(ConceptManager.buildQuery(ds),key), "Query for number field with isnull operator specified.");
       
       key = {
           concept_id: 50,
           datatype: "number",
           id: 157,
           operator: "-isnull",
           value: true
       };
       ds = {
           '50_157_operator': "-isnull"
       };
       ok(equivalent(ConceptManager.buildQuery(ds),key), "Query for number field with negated isnull operator specified.");
       
   });
   
   test("Query with conditions applied to variable fields.",1,function(){
       ConceptManager.show(criteria[1]);
       
       key = {
           children:[
                {
                    concept_id: 1,
                    id: 143,
                    operator: "exact",
                    value: true
                },
                {
                    concept_id: 1,
                    datatype: "number",
                    id: 151,
                    id_choices: [
                        "142",
                        "151",
                        "152"
                    ],
                    operator: "range",
                    value: [
                       24.7,
                       50.6
                    ]
                }
           ],
           concept_id: 1,
           type: "and"
       };
       ds = {
           '1_142OR151OR152_input0': "24.7",
           '1_142OR151OR152_input1': "50.6",
           '1_142OR151OR152_operator': "range",
           '1_143': true,
           '142OR151OR152': "151"
       };
       ok(equivalent(ConceptManager.buildQuery(ds),key), "Query for number with conditional field set to 152 and range operator selected. Additional boolean field set to true.");
       
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
