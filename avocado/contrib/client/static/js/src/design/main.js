require(['design/search', 'design/views'], function(search, views) {
   
    $(function() {
        search.init();
        // The view manager needs to know where in the DOM to place certain things
        var pluginTabs = $('#plugin-tabs'),
            pluginPanel = $('#plugin-panel'),
            pluginTitle = $('#plugin-title'),
            pluginDynamicContent = $('#plugin-dynamic-content'),
            pluginStaticContent = $('#plugin-static-content');
    
        // Create an instance of the viewManager object. Only do this once.
        var viewManager = new views.manager(pluginPanel, pluginTitle, pluginTabs, pluginDynamicContent,
            pluginStaticContent);

        var scopeButton = $('#scope'),
            scopeMenu = $('#scope-menu');

        scopeButton.toggle(function(evt) {
            scopeButton.addClass('selected');
            scopeMenu.show();
            return false;
        }, function(evt) {
            scopeButton.removeClass('selected');
            scopeMenu.hide();
            return false;
        });

        $('[data-model=category]').live('click', function(evt) {
            var target = $(this);
            target.trigger('search_criteria', target.data('name'));
            return false;
        });
    
        $('[data-model=criterion]').live('click', function(evt) {
            evt.preventDefault();
            var target = $(this);

            target.trigger('collapse_search');

            $.ajax({
                url: target.attr('data-uri'),
                dataType:'json',
                success: function(json) {
                    pluginPanel.fadeIn(100);
                    viewManager.show(json);
                }
            });
        });
    });
});
