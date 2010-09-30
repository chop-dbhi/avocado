require.def('design/search',
    ['rest/datasource', 'rest/renderer', 'design/templates'],

    function(datasource, renderer, templates) {

        function init() {

            var panel = $('#search-panel'),
                categories = $('#categories'),
                searchInput = $('#search'),
                searchForm = $('form', panel),

                criteria = $('#criteria');

            /*
            ** Initialize renderers for the available criterion options
            ** and the categories.
            */
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

            /*
            ** Initialize data sources for the available criterion options
            ** and the categories.
            */
            var src = {
                criteria: new datasource.ajax({
                    uri: criteria.attr('data-uri'),
                    success: function(json) {
                        if (json.length > 0)
                            rnd.criteria.render(json);
                        else
                            rnd.criteria.target.html('<em class="ht mg">No results found</em');
                    }
                }),
                categories: new datasource.ajax({
                    uri: categories.attr('data-uri'),
                    success: function(json) {
                        rnd.categories.render(json);
                    }
                })
            };

            // make initial request
            src.criteria.get();
            src.categories.get();
            
            panel.bind('activate.tabs', function(evt) {
                // remove ``active`` class from all *tabs*
                $('[data-model=category]', categories).removeClass('active');
                searchForm.removeClass('active');

                // activate the target
                $(evt.target).addClass('active');
                
            });
            
            categories.delegate('[data-model=category]', 'click', function(evt) {
                var target = $(this),
                    value = target.attr('data-search-term');

                // trigger events
                searchInput.trigger('search', value);
                target.trigger('activate');
                return false;
            });            
            
            searchInput.bind('focus', function() {
                searchForm.trigger('activate');
                return false;
            });

            // manual delegation, since there is a specific
            panel.bind('search', function(evt, value) {
                searchInput.trigger('search', value);
                return false;
            });

            searchInput.autocomplete({
                success: function(value, json) {
                    if (json.length > 0)
                        rnd.criteria.render(json);
                    else
                        rnd.criteria.target.html('<em class="ca mg">No results found for term "'+ value +'"</em>');
                }
            });
            

        };

        return {init: init};
    });
