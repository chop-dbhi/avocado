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
                                        
   module("Concept Manager Test");
   test('ConceptManager initialized correctly.', 1, function() {
      ok(ConceptManager.hasOwnProperty("show"), 'Has "show" method.');
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
