require.def('design/search',
    ['rest/datasource', 'rest/renderer', 'design/templates'],

    function(datasource, renderer, templates) {

        function init() {

            var content = $('#content'),
                categories = $('#categories'),
                searchInput = $('#search'),
                searchForm = $('#search-panel form'),
                pluginPanel = $('#plugin-panel'),

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

            content.bind('activate-tab', function(evt) {
                // remove ``active`` class from all *tabs*
                var target = $(evt.target);

                categories.children().removeClass('active');
                searchForm.removeClass('active');

                target.addClass('active');

                content.active_tab = target; 
                
                // check to see if a ``concept_id`` exists for this tab.
                // attempt to show the concept is so.

                var id = target.data('concept_id');

                if (id) {
                    pluginPanel.show();
                    content.trigger('activate-criterion', [id]);
                } else {
                    pluginPanel.hide();
                }

                return false;
            });
            
            categories.delegate('[data-model=category]', 'click', function(evt) {
                var target = $(this),
                    value = target.attr('data-search-term');

                // trigger events
                searchInput.trigger('search', value);
                target.trigger('activate-tab');
                return false;
            });            

            /*
             * handles taking a criterion id and set it as an attribute on the
             * active tab.
             */
            content.bind('setid-tab', function(evt, id) {
                content.active_tab.data('concept_id', parseInt(id));
                return false;
            });

            searchInput.bind('focus', function(evt) {
                searchForm.trigger('activate-tab');
                searchInput.trigger('search', searchInput.val());
            }).focus();

            searchForm.bind('click', function(evt) {
                searchInput.focus();
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
                    return false;
                }
            }, null, 200);
            


        }

        return {init: init};
    });
