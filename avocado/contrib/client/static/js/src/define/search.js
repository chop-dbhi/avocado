require.def('define/search',
    ['rest/datasource', 'rest/renderer', 'define/templates'],

    function(datasource, renderer, templates) {

        function init() {

            var content = $('#content'),
                tabs = $('#tabs'),
                searchInput = $('#search'),
                searchForm = $('#search-panel form'),
                pluginPanel = $('#plugin-panel'),
                criteria = $('#criteria').children();

            /*
             * Manages the tabs and keeps them in sync with the content area
             * based on the users interactions.
             */
            content.bind('activate-tab', function(evt) {
                var target = $(evt.target),
                    value = target.attr('data-search');

                if (target.is('form'))
                    value = searchInput.val();

                // activate target, deactivate other tabs
                target.addClass('active')
                    .siblings().removeClass('active');

                content.activetab = target; 
                
                // check to see if a ``concept_id`` exists for this tab.
                // attempt to show the concept is so.
                var id = target.data('concept_id');

                if (id) {
                    pluginPanel.show();
                    content.trigger('activate-criterion', [id]);
                } else {
                    pluginPanel.hide();
                }

                // triggers a canned search based on the object's search
                // term is provides. the ``true`` tells the search to cache
                // the results
                searchInput.trigger('search', [value, true]);

                return false;
            });
            
            /*
             * Bind the click event for tabs to activate them.
             */
            tabs.delegate('.tab', 'click', function(evt) {
                $(this).trigger('activate-tab');
                return false;
            });            

            /*
             * Binds the focus event for the search input to handle
             * keyboard tabbing.
             */
            searchInput.bind('focus', function(evt) {
                searchForm.trigger('activate-tab');
            }).focus();

            /*
             * Handles setting the criterion id currently in view for a
             * particular tab. This is to ensure once the user comes back
             * to the tab, the expected criterion will be shown.
             */
            content.bind('setid-tab', function(evt, id) {
                content.activetab.data('concept_id', parseInt(id));
                return false;
            });

            /*
             * The search acts on all criteria that is present for the user.
             * each search returns a list of ids that can be used to filter
             * down the list of criteria. the server hit is necessary to
             * utilize the database fulltext search, but it is uneccesary to
             * re-render the criteria every time.
             */
            searchInput.autocomplete({
                success: function(value, json) {
                    criteria.addClass('hd');
                    for (var i = 0; i < json.length; i++)
                        criteria.filter('[data-id='+json[i]+']').removeClass('hd'); 
                    return false;
                }
            }, null, 50);
            


        }

        return {init: init};
    });
