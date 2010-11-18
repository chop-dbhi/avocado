// report/table

require.def(
    
    'report/table',
    
    ['rest/datasource', 'rest/renderer', 'report/templates'],

    function(m_datasource, m_renderer, m_templates) {

        // TODO remove hardcoded URL
        var EMPTY_RESULTS = '<h1 class="ca info">No results match your conditions. ' +
            '<a href="' + URLS.define + '">Refine your conditions</a>.</h1>';

        function init() {
            var firstRequest = true;

            var body = $('body'),                       // event binding
                content = $('#content'),                // resizing
                report = $('#report'),                  // event binding, resizing, unhiding
                info = $('#report-info'),               // unhiding
                conditionsText = $('#conditions-text'), // unhiding
                toolbars = report.find('.toolbar'),     // unhiding
                table = $('#table'),                    // resizing, unhiding
                thead = table.find('thead tr'),         // event delegation, data loading
                tbody = table.find('tbody'),            // data loading
                per_page = $('.per-page'),              // data loading
                pages = $('.page-links'),               // data loading
                unique = $('.unique-count'),            // data loading
                count = $('.count');                    // data loading

            /*
             * The renderers necessary for rendering the response data into HTML
             * templates.
             *
             * ``table_header`` - renders the table header that displays column
             * names and the column ordering.
             *
             * ``table_rows`` - renders the table rows that displays the data.
             *
             * ``pages`` - renders the page links relative the entire result
             * set.
             */
            var rnd = {
                table_header: new m_renderer.template({
                    target: thead,
                    template: m_templates.header
//                    replace: 'append'
                }),
                table_rows: new m_renderer.template({
                    target: tbody,
                    template: m_templates.row
                }),
                pages: new m_renderer.template({
                    target: pages,
                    template: m_templates.pages
                })
            };


            /*
             * The data sources which make requests and handles the body of the
             * response.
             *
             * ``table_header`` - requests the latest header data.
             *
             * ``table_rows`` - requests the latest results for the report in
             * view.
             */
            var src = {
                scope_info: new m_datasource.ajax({
                    uri: API_URLS.scope,
                    success: function(json) {
                        if (json.text) { 
                            var t = '';
                            if (typeof json.text === 'string') {
                                t = '<li>' + json.text + '</li>';
                            } else {
                                var conditions = json.text.conditions;
                                for (var i=0; i < conditions.length; i++)
                                    t += '<li>' + conditions[i] + '</li>';
                            }
                            conditionsText.html('<ul>' + t + '</ul>');
                        }
                    }
                }),

                table_header: new m_datasource.ajax({
                    uri: API_URLS.perspective,
                    success: function(json) {
//                        rnd.table_header.target.html('<th><input type="checkbox"></th>');
                        rnd.table_header.render(json.header);
                    }
                }),

                table_rows: new m_datasource.ajax({
                    uri: API_URLS.report,
                    success: function(json) {
                        if (json.rows.length === 0) {
                            $('.content').html(EMPTY_RESULTS);
                            return;
                        }

                        rnd.table_rows.render(json.rows); 

                        if (json.pages) {
                            rnd.pages.render(json.pages);
                        } else {
                            if (firstRequest)
                                per_page.hide();
                            rnd.pages.target.hide();
                        }

                        if (json.unique)
                            unique.html(json.unique);

                        if (json.count)
                            count.html(json.count);
                        
                        if (json.per_page)
                            per_page.val(json.per_page);

                        report.trigger('resize-report');

                        /*
                         * Unhide necessary elements on first request.
                         */
                        if (firstRequest) {
                            firstRequest = false;
                            setTimeout(function() {
                                info.show();
                                toolbars.show();
                                table.show();
                            }, 500);
                        }
                    }
                })
            };

            /*
             * Make initial requests on initialization.
             */
            src.scope_info.get();
            src.table_header.get();
            src.table_rows.get();

            report.bind('resize-report', function(evt) {
                var minWidth = 900,
                    rInnerWidth = report.innerWidth(),
                    tOuterWidth = table.outerWidth(true)+20; // padding is not usable

                // do not grow past window width. take into account the padding
                nInnerWidth = Math.min(tOuterWidth, window.innerWidth-30);
                nInnerWidth = Math.max(minWidth, nInnerWidth);
 
                // determine the difference. half of it needs to be added
                // to the margin-right offset
                if (nInnerWidth == rInnerWidth)
                    return;

                half = (nInnerWidth - rInnerWidth) / 2.0;

                nLeft = parseInt(content.css('margin-left').match(/-?\d+/)[0]) - half;

                content.animate({
                    marginLeft: nLeft
                });

                report.animate({
                    width: nInnerWidth
                });
            });

            var resizeTimeOut;
            $(window).resize(function() {
                clearTimeout(resizeTimeOut);
                resizeTimeOut = setTimeout(function() {
                    report.trigger('resize-report');
                }, 200);
            });

             /*
             * Define primary event that handles fetching data.
             */
            body.bind('update.report', function(evt, params) {
                src.table_rows.get(params);
                return false;
            });

            body.bind('update.perspective', function(evt, params) {
                $.putJSON(API_URLS.perspective, JSON.stringify(params), function() {
                    body.trigger('update.report');
                    if ('columns' in params)
                        src.table_header.get(); 
                });
                return false;
            });

          
            /*
             * Hook up the elements that change the number of rows per page.
             */
            report.delegate('.per-page', 'change', function(evt) {
                if (this.value)
                    body.trigger('update.report', {'n': this.value});
                return false;
            });

            /*
             * This implementation does *not* currently support multiple column
             * sorting. The only change needed is to grab all of the header
             * directions and pass it to the server.
             */
            thead.delegate('.header', 'click', function(evt) {
                var dir, target = $(this), id = target.attr('data-id'),
                    siblings = target.siblings();

                // reset siblings to no ordering
                siblings.removeClass('asc').removeClass('desc');

                if (target.hasClass('asc')) {
                    target.removeClass('asc').addClass('desc');
                    dir = 'desc';
                } else if (target.hasClass('desc')) {
                    target.removeClass('desc');
                    dir = '';
                } else {
                    target.addClass('asc');
                    dir = 'asc';
                }

                body.trigger('update.perspective', [{'ordering': [[id, dir]]}]);
                return false;
            });
            
            /*
             * Hook up the elements that change the page.
             */
            pages.delegate('a', 'click', function(evt) {
                body.trigger('update.report', {'p': this.hash.substr(1)});
                return false;
            });
        };

        return {init: init};
    }
);
