require.def('design/search',
    ['rest/datasource', 'rest/renderer', 'design/templates'],

    function(datasource, renderer, templates) {

        function init() {

            var panel = $('#search-panel'),
                criteria = $('#criteria'),
                categories = $('#categories'),
                search = $('#search'),
                expand = $('#expand-search');

            var rnd = {
                criteria: new renderer.template({
                    target: criteria,
                    template: templates.criteria.list
                }),
                categories: new renderer.template({
                    target: categories,
                    template: templates.categories.list
                })
            };

            var src = {
                criteria: new datasource.ajax({
                    uri: criteria.attr('data-uri'),
                    callback: function(json) {
                        rnd.criteria.render(json);
                    }
                }),
                categories: new datasource.ajax({
                    uri: categories.attr('data-uri'),
                    callback: function(json) {
                        rnd.categories.render(json);
                    }
                })
            };

            // make initial request
            src.criteria.get();
            src.categories.get();

            panel
                .data('collapsed', true)
                .bind('load_criteria', function(evt, params) {
                    src.criteria.get(null, params);
                    return false;
                })

                .bind('search_criteria', function(evt, term) {
                    search.val(term).keyup();
                    return false;
                })

                .bind('expand_search', function(evt) {
                    expand.html('&laquo;');
                    criteria.animate({width: 498}, 400);
                    panel.animate({width: 744}, 400)
                        .data('collapsed', false);
                    setTimeout(function() {
                        categories.fadeIn(100);
                    }, 400);
                    return false;
                })
                
                .bind('collapse_search', function(evt) {
                    expand.html('&raquo;');
                    categories.fadeOut(100);
                    setTimeout(function() {
                        criteria.animate({width: 180}, 400);
                        panel.animate({width: 200}, 400)
                            .data('collapsed', true);                        
                    }, 100);
                    return false;
                })
                
                .bind('toggle_search', function(evt) {
                    var collapsed = panel.data('collapsed');
                    if (collapsed)
                        panel.trigger('expand_search');
                    else
                        panel.trigger('collapse_search');
                    return false;
                });
                        

            search.autocomplete({
                success: function(query, json) {
                    rnd.criteria.render(json);
                }
            });

            expand.click(function(evt) {
                panel.trigger('toggle_search');
                return false;
            });
        };

        return {init: init};
    }
);
