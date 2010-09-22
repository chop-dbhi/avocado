require.def('design/search',
    ['rest/datasource', 'rest/renderer', 'design/templates'],

    function(datasource, renderer, templates) {

        function init() {

            var body = $('body'),
                panel = $('#search-panel'),
                criteria = $('#criteria'),
                categories = $('#categories'),
                search = $('#search');

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
                        if (json.length > 0)
                            rnd.criteria.render(json);
                        else
                            rnd.criteria.target.html('<em class="ht mg">No results found</em');
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
                var target = $(this),
                    value = target.attr('data-search-term');
                search.trigger('search', value);
                target.siblings().removeClass('active');
                target.addClass('active');
                return false;
            });            

            // manual delegation, since there is a specific
            panel.bind('search', function(evt, value) {
                search.trigger('search', value);
                return false;
            });

            search.autocomplete({
                success: function(value, json) {
                    if (json.length > 0)
                        rnd.criteria.render(json);
                    else
                        rnd.criteria.target.html('<em class="ca mg">No results found for term "'+ value +'"</em>');
                }
            });
        };

        return {init: init};
    }
);
