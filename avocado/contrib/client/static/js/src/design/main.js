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

        // TODO change this into a jQuery extension or something..
        (function() {
            var cache = {},
                re = 10,
                ft = 100;
            
            function get(e) {
                if (!cache[e.id]) {
                    var t = $(e),
                        m = $(t.attr('data-for')),
                        mw = m.outerWidth();
                    
                    le = document.width - t.offset().left;
                    // if menu will be at least up against the left edge
                    if (re + mw >= le)
                        m.css('right', re);
                    // default to up against left edge assuming it doesn't fall
                    // off the right
                    else
                        m.css('right', le - mw);
                    cache[e.id] = [t, m];
                }
                return cache[e.id];
            };
            
            function hide() {
                for (var e in cache) {
                    cache[e][1].hide();
                    cache[e][0].removeClass('selected');
                }
            };

            $('#tools').delegate('span', 'click', function(evt) {
                var e = get(this), t = e[0], m = e[1];
                
                if (t.hasClass('selected')) {
                    m.fadeOut(ft);
                    t.removeClass('selected');
                } else {
                    hide();
                    t.addClass('selected');
                    m.fadeIn(ft);
                }
            });            
        })();

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
