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
                    template: templates.criteria,
                    bindData: true
                }),
                categories: new renderer.template({
                    target: categories,
                    template: templates.categories
                })
            };

            /*
            ** Initialize data sources for the available criterion options
            ** and the categories.
            */
            var src = {
                criteria: new datasource.ajax({
                    uri: searchForm.attr('action'),
                    success: function(json) {
                        rnd.criteria.render(json);
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

            /*
             * the search acts on all criteria that is present for the user.
             * each search returns a list of ids that can be used to filter
             * down the list of criteria. the server hit is necessary to
             * utilize the database fulltext search, but it is uneccesary to
             * re-render the criteria every time.
             */
            searchInput.autocomplete({
                success: function(value, json) {
                    var objs = $('[data-model=criterion]', criteria).removeClass('inview');
                    for (var i = 0; i < json.length; i++) {
                        objs.jdata('id', json[i]).addClass('inview');
                    }
                }
            });
            

        };

        return {init: init};
    });
