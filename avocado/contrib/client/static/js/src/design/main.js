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

        var tools = $('#tools').children(),
            toolMenus = $('#tool-menus').children();

        var mid;
        tools.toggle(function(evt) {
            tools.removeClass('selected');
            toolMenus.hide();
            var target = $(this);
            mid = '#' + target.attr('id') + '-menu';
            $(mid).show()
            target.addClass('selected');
            return false;
        }, function() {
            var target = $(this);
            mid = '#' + target.attr('id') + '-menu';
            $(mid).hide()
            target.removeClass('selected');
        })

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
