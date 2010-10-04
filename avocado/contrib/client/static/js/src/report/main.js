require.def('report/main',
    ['rest/datasource', 'rest/renderer', 'report/templates'],

    function(datasource, renderer, templates) {

        $(function() {
            var report = $('#report'),
                table = $('#table'),
                header = $('thead tr', table),
                body = $('tbody', table),
                per_page = $('.per-page'),
                pages = $('.page-links'),
                unique = $('.unique-count'),
                count = $('.count');

            var search = $('#search'),
                columns = $('#columns'),
                active_columns = $('#active-columns');
     
            var rnd = {
                table_header: new renderer.template({
                    target: header,
                    template: templates.header,
                    replace: 'append'
                }),
                table_rows: new renderer.template({
                    target: body,
                    template: templates.row
                }),
                pages: new renderer.template({
                    target: pages,
                    template: templates.pages
                }),
            };

            var src = {
                table_rows: new datasource.ajax({
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
        });
    });
