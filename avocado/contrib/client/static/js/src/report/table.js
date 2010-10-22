// report/table

require.def(
    
    'report/table',
    
    ['rest/datasource', 'rest/renderer', 'report/templates'],

    function(m_datasource, m_renderer, m_templates) {

        function init() {
            var body = $('body'),
                content = $('#content'),
                resize = $('#resize'),
                report = $('#report'),
                thead = $('#table thead tr'),
                tbody = $('#table tbody'),
                per_page = $('.per-page'),
                pages = $('.page-links'),
                unique = $('.unique-count'),
                count = $('.count');

            var rnd = {
                table_header: new m_renderer.template({
                    target: thead,
                    template: m_templates.header,
                    replace: 'append'
                }),
                table_rows: new m_renderer.template({
                    target: tbody,
                    template: m_templates.row
                }),
                pages: new m_renderer.template({
                    target: pages,
                    template: m_templates.pages
                }),
            };

            var report_uri = report.attr('data-uri');

            var src = {
                table_rows: new m_datasource.ajax({
                    uri: report_uri,
                    success: function(json) {
                        rnd.table_rows.render(json.rows);

                        // TODO clean up
                        if (json.header) {
                            rnd.table_header.target.html('<th><input type="checkbox"></th>');
                            rnd.table_header.render(json.header);
                        }

                        report.trigger('resize-report');

                        if (json.pages)
                            rnd.pages.render(json.pages);

                        if (json.unique)
                            unique.html(json.unique);

                        if (json.count)
                            count.html(json.count);


                        if (json.per_page)
                            per_page.val(json.per_page);
                    }
                })
            };

            src.table_rows.get();


            report.bind('resize-report', function(evt) {
                var table = $('#table'),
                    minWidth = 850,
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
                    'margin-left': nLeft
                });

                report.animate({
                    'width': nInnerWidth,
                });
            });

            resize.bind('click', function(evt) {
                report.trigger('resize-report');
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
          
            /*
             * Hook up the elements that change the number of rows per page.
             */
            report.delegate('.per-page', 'change', function(evt) {
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

                body.trigger('update.perspective', {'ordering': [[id, dir]]});
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
