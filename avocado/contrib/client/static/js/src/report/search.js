// report/search

require.def(
    
    'report/search',

    ['rest/datasource', 'rest/renderer', 'report/templates', 'lib/jquery.ui', 'lib/json2'],

    function(m_datasource, m_renderer, m_templates) {

        function init() {

            var body = $('body'),
                columns = $('#columns'),
                active_columns = $('#active-columns'),

                searchdialog = $('#search-dialog'),
                searchinput = $('#search'),
                searchform = $('form', searchdialog),
                searchbutton = $('#search-button');

            var perspective_uri = searchdialog.attr('data-uri'),
                column_uri = searchform.attr('action');

            /*
             * Pre-setup and event handler binding
             */
            body.bind('update.perspective', function(evt, params) {
                $.putJSON(perspective_uri, JSON.stringify(params), function() {
                    body.trigger('update.report');
                });
                return false;
            });
 
            searchdialog.cache = {};

            searchdialog.get = function(id) {
                if (!searchdialog.cache[id]) {
                    var sel = '[data-model=column][data-id=' + id + ']'; 

                    searchdialog.cache[id] = {
                        'src': columns.find(sel),
                        'tgt': active_columns.find(sel)
                    };
                }
                return searchdialog.cache[id];
            };

            searchdialog.bind('addall.column', function(evt, id) {
                var category = $('[data-model=category][data-id=' + id + ']'),
                    columns = category.find('li');
                
                category.hide();
                for (var i=columns.length; i--;)
                    searchdialog.trigger('add.column', [$(columns[i]).attr('data-id')]);

                return false;
            });

            searchdialog.bind('add.column', function(evt, id) {
                map = searchdialog.get(id);

                map.src.removeClass('active');

                // check to see if this is the last child being 'activated',
                // if so then hide the category
                var sibs = map.src.siblings('.active:not(.filtered)');
                if (sibs.length == 0)
                    map.src.parents('[data-model=category]').hide();

                // detach from wherever it is and append it to the end of the
                // list. since non-active columns are not shown, this will be
                // perceived as being added to the end of the 'visible' list
                active_columns.append(
                    map.tgt.detach().addClass('active')
                );

                return false;
            });

            searchdialog.bind('remove.column', function(evt, id) {
                map = searchdialog.get(id);

                map.tgt.removeClass('active');
                map.src.addClass('active').parents('[data-model=category]').show();

                return false;
            });

            searchdialog.bind('search.column', function(evt, value) {
                searchinput.trigger('search', value);
                return false;
            });

            searchdialog.bind('save.column', function(evt) {
                var children = active_columns.children('.active'),
                    ids = $.map(children, function(e, i) {
                        return parseInt($(e).attr('data-id'));
                    });

                body.trigger('update.perspective', [{columns: ids}]);
                return false;
            });


            var rnd = {
                columns: new m_renderer.template({
                    target: columns,
                    template: m_templates.columns
                }),
                active_columns: new m_renderer.template({
                    target: active_columns,
                    template: m_templates.active_columns
                })
            };

            var src = {
                columns: new m_datasource.ajax({
                    uri: column_uri,
                    success: function(json) {
                        rnd.columns.render(json);
                        
                        // only the columns are needed for setting up the list
                        // of potential 'active columns'
                        var columns = json.map(function(e) {
                            return e['columns'];
                        });
                        columns = Array.prototype.concat.apply([], columns);
                        rnd.active_columns.render(columns);

                        src.perspective.get();
                    }
                }),
                perspective: new m_datasource.ajax({
                    uri: perspective_uri,
                    success: function(json) {
                        if (json.store) {
                            var rcols = json.store.columns;
                            for (var i=0; i < rcols.length; i++)
                                searchdialog.trigger('add.column', [rcols[i]]);
                        }
                    }
                }) 
            };

            src.columns.get();

            searchinput.autocomplete({
                success: function(value, json) {
                    var objs = $('[data-model=column]', columns).addClass('filtered');
                    for (var i = 0; i < json.length; i++)
                        objs.jdata('id', json[i]).removeClass('filtered');

//                    rnd.criteria.target.html('<em class="ca mg">no results found for term "'+ value +'"</em>');
                }
            });

            columns.delegate('.add-column', 'click', function(evt) {
                var id = evt.target.hash.substr(1);
                searchdialog.trigger('add.column', [id]);
                return false;
            });

            columns.delegate('.add-all', 'click', function(evt) {
                var id = evt.target.hash.substr(1);
                searchdialog.trigger('addall.column', [id]);
                return false;
            });

            active_columns.delegate('.remove-column', 'click', function(evt) {
                var id = evt.target.hash.substr(1);
                searchdialog.trigger('remove.column', [id]);
                return false;
            });

            searchdialog.dialog({
                autoOpen: false,
                draggable: true,
                resizable: true,
                title: 'Show/Hide Columns',
                height: 550,
                width: 700,
                minWidth: 700,
                buttons: {
                    Cancel: function() {
                        searchdialog.dialog('close');
                    },
                    Save: function() {
                        searchdialog.trigger('save.column');
                        searchdialog.dialog('close');
                    }
                }
            });

            /*
             * The active columns list is sortable to easily define the order
             * of display of the columns. That is, the order defined in the
             * list (top-bottom) translates to the order in the table
             * (left-right).
             */
            active_columns.sortable({
                placeholder: 'placeholder',
                forcePlaceholderSize: true,
                forceHelperSize: true,
                opacity: 0.5,
                cursor: 'move',
                tolerance: 'intersect'
            });

            searchbutton.bind('click', function(evt) {
                searchdialog.dialog('open');
            });
        };

        return {init: init};
    }
);
