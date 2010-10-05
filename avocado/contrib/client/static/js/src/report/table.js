// report/table

require.def(
    
    'report/table',
    
    ['rest/datasource', 'rest/renderer', 'report/templates'],

    function(m_datasource, m_renderer, m_templates) {

        function init() {
            var report = $('#report'),
                table = $('#table'),
                header = $('thead tr', table),
                body = $('tbody', table),
                per_page = $('.per-page'),
                pages = $('.page-links'),
                unique = $('.unique-count'),
                count = $('.count');

            var rnd = {
                table_header: new m_renderer.template({
                    target: header,
                    template: m_templates.header,
                    replace: 'append'
                }),
                table_rows: new m_renderer.template({
                    target: body,
                    template: m_templates.row
                }),
                pages: new m_renderer.template({
                    target: pages,
                    template: m_templates.pages
                }),
            };

            var src = {
                table_rows: new m_datasource.ajax({
                    uri: report.attr('data-uri'),
                    success: function(json) {
                        rnd.table_rows.render(json.rows);
                        rnd.table_header.target.html('<th><input type="checkbox"></th>');
                        rnd.table_header.render(json.header);

                        /*
                         * update the counts reflecting the rows
                         */
                        unique.html(json.unique);
                        count.html(json.count);

                        /*
                         * handle a few optional variables
                         */
                        if (json.pages)
                            rnd.pages.render(json.pages);

                        if (json.per_page)
                            per_page.val(json.per_page);
                    }
                })
            };

            src.table_rows.get();
            
            /*
             * Hook up the elements that change the number of rows per page.
             */
            report.delegate('.per-page', 'change', function(evt) {
                report.trigger('update.report', {'per_page': this.value});
                return false;
            });
            
            /*
             * Hook up the elements that change the page.
             */
            pages.delegate('a', 'click', function(evt) {
                report.trigger('update.report', {'page': this.hash.substr(1)});
                return false;
            });
            
            /*
             * Define primary event that handles fetching data.
             */
            report.bind('update.report', function(evt, params) {
                src.table_rows.get(params);
                return false;
            });

        };

        return {init: init};
    }
);

///*
//** This is a page specific script which applies to the query reporting tool
//** regarding loading and manipulation of the data.
//*/
//
//var refreshRows,
//    $unsavedSetMsg,
//    $objSetInfo;
//
//(function() {
//    var $container,
//        $resultsHead,
//        $resultsBody,
//        $resultsCount,
//        headerTemplate,
//        rowTemplate;
//
//    var prepareHeader = function(obj, ctemplate) {
//        /*
//        ** Generates the table header given an object and compile template.
//        **
//        ** `obj' should be a qualified JSON object (an array) with a key-value for
//        ** a unique identifier in addtion to a key/value for the data itself.
//        */
//        if (!obj || !ctemplate)
//            throw 'an object and a compiled template must be supplied';
//    
//        var header = $.jqoteobj(ctemplate, obj);
//
//        $.each(header.children('.header'), function(i) {
//            $(this).data('pk', obj.header[i].pk);
//        });
//
//        return header;
//    };
//
//    var prepareRows = function(obj, ctemplate) {
//        /*
//        ** This function manages generating the DOM elements to be appended
//        ** to the results table. The optional `replace' argument will replace
//        ** the existing elements in the results table instead of appending.
//        ** This is useful for page refreshes.
//        **
//        ** `obj' should be a qualified JSON object (an array) with a key-value for
//        ** a unique identifier in addtion to a key/value for the data itself.
//        */
//        if (!obj || !ctemplate)
//            throw 'an object and a compiled template must be supplied';
//
//        // compile data into a new jquery object
//        var rows = $.jqoteobj(ctemplate, obj);
//
//        // bind data to each DOM element
//        $.each(rows, function(i) {
//            $(this).data('pk', obj[i].pk);
//        });
//            
//        return rows;
//    };
//
//    var getRows = function(obj, key, value) {
//        /*
//        ** Simple helper function implement the $().jdata extension.
//        */
//        return obj.jdata(key, value);
//    };
//
//    var removeRows = function(obj) {
//        /*
//        ** Takes a jQuery object which are the rows that are intended to be
//        ** removed.
//        */
//        // hide initially for instant user feedback
//        obj.hide();
//    
//        var ids = $.map(obj, function(e) {
//            return $(e).data('pk');
//        });
//        
//        var data = {
//            'removed_ids':  ids.join(',')
//        };
//        
//        refreshRows(null, 'POST', data, function(json) {
//            if (json.unsaved == false) {
//                $ajaxMsg.addClass('success').html('Saved.').show();
//                setTimeout(function() {
//                    $ajaxMsg.hide().removeClass('success');
//                }, 2500);
//            }
//        }, function() {
//            obj.show();
//        });
//    };
//
//    var sortRows = function() {
//        /*
//        ** The hook that builds the necessary GET data for sending a request
//        ** to "sort the results by column."
//        */
//        var e,
//            data = [],
//            columns = $('#results .header');
//
//        for (var i = 0; i < columns.length; i++) {
//            e = $(columns[i]);
//            if (e.hasClass('asc'))
//                data.push(e.data('pk') + '|asc');
//            else if (e.hasClass('desc'))
//                data.push(e.data('pk') + '|desc');
//        }
//    
//        refreshRows(null, null, {'column_ordering': data.join(',')});
//    };
//
//    refreshRows = function(url, type, data, success, error) {
//        /*
//        ** This is the interface in which an AJAX request is made. Any hook that
//        ** builds up request data must call this function to actually make the
//        ** request.
//        **
//        ** `page' defines the page of results that is to be returned. defaults to
//        ** `CURRENT_PAGE'.
//        **
//        ** `type' defines the request type, use 'POST' when altering the data in
//        ** any way. default is 'GET'.
//        **
//        ** `data' represents the GET or POST data that is being sent to the server.
//        ** defaults to an empty object.
//        **
//        ** `success' defines an "on success" handler that will be called
//        ** after the results have been loaded. defaults to an empty function.
//        **
//        ** `error' defines an "on error" handler that will be called during
//        ** the error handling for the AJAX response.
//        */
//    
//        url = url || PATIENT_LIST_URL + '?page=' + CURRENT_PAGE;
//        type = type || 'GET';
//        data = data || {};
//        success = success || function() {};
//        error = error || function() {};
//        
//        $container.block();
//    
//        $.ajax({
//            type: type,
//            url: url,
//            data: data,
//            success: function(json) {
//                ajaxSuccess(json);
//
//                if (json.rows) {
//                    if (json.header) {
//                        var header = prepareHeader(json, headerTemplate);
//                        $resultsHead.html(header);
//                    }
//                    
//                    if (json.unsaved == true)
//                        $unsavedSetMsg.show();
//                    else
//                        $unsavedSetMsg.hide();
//                
//                    var rows = prepareRows(json.rows, rowTemplate);                
//                    $resultsBody.html(rows);
//
//                    $resultsCount.html(json.count);
//                    $paginators.html(json.paginator); 
//                } else {
//                    // clear everything and display simple message
//                    $toolbars.hide();
//                    $resultsCount.html('No hits');
//                    $container.children('.content').html('Try <a href="' +
//                        SITE_PREFIX + '/query/">refining your query</a> to ' +
//                        'be less specific.');
//                }
//                success(json);
//                $container.unblock();
//            },
//            error: function() {
//                error();
//                $container.unblock();
//            }
//        });
//    };
//
//    $(document).ready(function() {
//        
//        $unsavedSetMsg = $('#unsaved-set-message');
//        $objSetInfo = $('#patient-set-info');
//        $container = $('#results-container');
//        $resultsCount = $('#result-count');
//        $resultsHead = $('#results thead');
//        $resultsBody = $('#results tbody');
//        $paginators = $('.paginator');
//        $toolbars = $('.toolbar');
//    
//        // compiled templates for jqote
//        headerTemplate= $.jqotec('#header-template');
//        rowTemplate = $.jqotec('#row-template');
//
//        /* 
//        ** Sets up the necessary binds for selecting and de-selecting similar
//        ** rows via their checkboxes. A row will be selected if directly checked
//        ** or if a sibling row with the same `pk' value is checked.
//        */
//        $('#results :checkbox').live('click', function() {
//            var siblings,
//                $checkboxes,
//                $this = $(this),
//                value = $this.val() == 'on' ? null : $this.val();
//                
//            if (!value)
//                $checkboxes = $('#results :checkbox');
//            else
//                $checkboxes = $('#results :checkbox[value=' + value + ']');
//        
//            if ($this.attr('checked') == true) {
//                // select all rows that have this and check the boxes
//                $checkboxes.attr('checked', true)
//                    .parents('tr').addClass('selected');
//            } else {
//                $checkboxes.attr('checked', false)
//                    .parents('tr').removeClass('selected');
//            }
//        });
//
//
//        /*
//        ** Sets up the binds for the table header where the column names are
//        ** defined. Each column triggers a "column sort" action. The timeout
//        ** has been added since a user need to cycle through to get to a specific
//        ** ordering i.e. "ascending", "descending" or "no sort".
//        **
//        ** NOTE: this is wrapped in a closure to prevent `timer' from conflicting
//        ** else where.
//        */
//        (function() {
//            var timer = null;
//            $('#results .header').live('click', function() {
//                if (timer)
//                    clearTimeout(timer);
//
//                var $this = $(this);
//
//                if ($this.hasClass('asc'))
//                    $this.removeClass('asc').addClass('desc');
//                else if ($this.hasClass('desc'))
//                    $this.removeClass('desc');
//                else
//                    $this.addClass('asc');
//        
//                // remove this line to allow for multi-column sorting
//                $this.siblings('.header').removeClass('asc desc');
//
//                timer = setTimeout(function() {
//                    sortRows();
//                }, 600);
//            });
//        })();
//    
//        $('.remove-selected').click(function(evt) {
//            var rows = $resultsBody.children('.selected');
//            removeRows(rows);
//        });
//    
//        $('.save-patient-set').click(function(evt) {
//            evt.preventDefault();
//            $saveDialog.dialog('open');
//        });
//
//        $('.delete-patient-set').click(function(evt) {
//            evt.preventDefault();
//            $deleteDialog.dialog('open');
//        });
//
//        $('.paginator .page-link').live('click', function(evt) {
//            evt.preventDefault();
//            refreshRows(this.href, 'GET');
//        });
//    
//        refreshRows(null, null, null, function() {
//            $container.children().removeClass('hd');
//            $container.children('.content').fadeIn();
//        });
//    });
//})();
