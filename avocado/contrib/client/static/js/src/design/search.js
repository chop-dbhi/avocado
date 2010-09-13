require.def('design/search',
    ['rest/datasource', 'rest/renderer', 'design/templates'],

    function(datasource, renderer, templates) {

        function init() {

            var body = $('body'),
                panel = $('#search-panel'),
                criteria = $('#criteria'),
                categories = $('#categories'),
                search = $('#search');

            body.bind('delegate_search_select', function(evt, term) {
                var target, dterm;
                $('[data-search-select]').each(function() {
                    target = $(this);
                    dterm = target.attr('data-search-term').toLowerCase();
                    if (dterm == term.toLowerCase())
                        target.addClass('active');
                    else
                        target.removeClass('active');
                });
                return false;
            });

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
            
            categories.delegate('[data-model=category]', 'click', function(evt) {
                var target = $(this);
                target.trigger('search_criteria', target.attr('data-search-term'));
                return false;
            });            

            panel
                .bind('load_criteria', function(evt, params) {
                    src.criteria.get(null, params);
                    return false;
                })

                .bind('search_criteria', function(evt, term) {
                    search.val(term).keyup();
                    return false;
                });

            search.autocomplete({
                success: function(query, json) {
                    console.log(query);
                    rnd.criteria.render(json);
                    search.trigger('delegate_search_select', query);
                }
            });
        };

        return {init: init};
    }
);
