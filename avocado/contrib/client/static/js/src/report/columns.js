// report/columns

require.def(
    
    'report/columns',

    ['rest/datasource', 'rest/renderer', 'report/templates', 'lib/jquery.ui', 'lib/json2'],

    function(m_datasource, m_renderer, m_templates) {

        function init() {

            var body = $('body'),
                columns = $('#columns'),
                active_columns = $('#active-columns'),

                columnsdialog = $('#columns-dialog'),
                searchinput = $('#search'),
                searchform = $('form', columnsdialog),
                columnsbutton = $('#data-columns');


            columnsdialog.cache = {};

            columnsdialog.get = function(id) {
                if (!columnsdialog.cache[id]) {
                    var sel = '[data-model=column][data-id=' + id + ']'; 

                    columnsdialog.cache[id] = {
                        'src': columns.find(sel),
                        'tgt': active_columns.find(sel)
                    };
                }
                return columnsdialog.cache[id];
            };

            columnsdialog.bind('addall.column', function(evt, id) {
                var category = $('[data-model=category][data-id=' + id + ']'),
                    columns = category.find('.active:not(.filtered)');
                
                category.hide();
                for (var i=0; i < columns.length; i++)
                    columnsdialog.trigger('add.column', [$(columns[i]).attr('data-id')]);

                return false;
            });

            columnsdialog.bind('add.column', function(evt, id) {
                map = columnsdialog.get(id);

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

            columnsdialog.bind('remove.column', function(evt, id) {
                map = columnsdialog.get(id);

                map.tgt.removeClass('active');
                map.src.addClass('active').parents('[data-model=category]').show();

                return false;
            });

            columnsdialog.bind('removeall.column', function(evt) {
                for (var id in columnsdialog.cache)
                    columnsdialog.trigger('remove.column', [id]);

                return false;
            });

            columnsdialog.bind('search.column', function(evt, value) {
                searchinput.trigger('search', value);
                return false;
            });

            columnsdialog.bind('save.column', function(evt) {
                var children = active_columns.children('.active'),
                    ids = $.map(children, function(e, i) {
                        return parseInt($(e).attr('data-id'));
                    });

                body.trigger('update.perspective', [{columns: ids}]);
                return false;
            });

            columnsdialog.bind('filter.column', function(evt, id) {
                map = columnsdialog.get(id);
                map.src.addClass('filtered');
                var sibs = map.src.siblings('.active:not(.filtered)');
                if (sibs.length == 0)
                    map.src.parents('[data-model=category]').hide();
            });

            columnsdialog.bind('filterall.column', function(evt) {
                var objs = columns.find('[data-model=column]');
                for (var i = objs.length; i--;)
                    columnsdialog.trigger('filter.column', [$(objs[i]).attr('data-id')]);
                return false;
            });

            columnsdialog.bind('unfilter.column', function(evt, id) {
                map = columnsdialog.get(id);
                map.src.removeClass('filtered');
                map.src.parents('[data-model=category]').show();
                return false;
            });

            var src = {
                perspective: new m_datasource.ajax({
                    uri: API_URLS.perspective,
                    success: function(json) {
                        if (json.store) {
                            var rcols = json.store.columns;
                            for (var i=0; i < rcols.length; i++)
                                columnsdialog.trigger('add.column', [rcols[i]]);
                        }
                    }
                }) 
            };

            src.perspective.get();

            var descriptionBox = $('<div id="description"></div>')
                .appendTo('body');

            $('#columns').delegate('.actions > .info', 'mouseover', function() {
                var target = $(this).closest('li'),
                    offset = target.offset(),
                    width = target.outerWidth(),
                    description = target.children('.description').html();

                descriptionBox.html(description);
                descriptionBox.css({
                    left: offset.left + width + 20,
                    top: offset.top
                }).show();
            }).delegate('.actions > .info', 'mouseout', function() {
                descriptionBox.hide();
            });


            searchinput.autocomplete2({
                success: function(value, json) {
                    searchinput.trigger('filterall.column');
                    for (var i = 0; i < json.length; i++)
                        searchinput.trigger('unfilter.column', [json[i]]);
                }
            }, null, 50);

            columns.delegate('.add-column', 'click', function(evt) {
                var id = evt.target.hash.substr(1);
                columnsdialog.trigger('add.column', [id]);
                return false;
            });

            columns.delegate('.add-all', 'click', function(evt) {
                var id = evt.target.hash.substr(1);
                columnsdialog.trigger('addall.column', [id]);
                return false;
            });

            active_columns.delegate('.remove-column', 'click', function(evt) {
                var id = evt.target.hash.substr(1);
                columnsdialog.trigger('remove.column', [id]);
                return false;
            });

            columnsdialog.delegate('.remove-all', 'click', function(evt) {
                columnsdialog.trigger('removeall.column');
                return false;
            });

            columnsdialog.dialog({
                autoOpen: false,
                draggable: false,
                resizable: false,
                title: 'Add or Remove Columns from this Report',
                height: 600,
                width: 900,
                buttons: {
                    Cancel: function() {
                        columnsdialog.dialog('close');
                    },
                    'Update Columns': function() {
                        columnsdialog.trigger('save.column');
                        columnsdialog.dialog('close');
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
            }).disableSelection();

            columnsbutton.bind('click', function(evt) {
                columnsdialog.dialog('open');
            });
        };

        return {init: init};
    }
);
