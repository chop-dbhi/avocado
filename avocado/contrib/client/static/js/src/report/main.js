require.def('report/main',
    ['rest/datasource', 'rest/renderer', 'report/templates'],

    function(datasource, renderer, templates) {

        $(function() {
            var report = $('#report'),
                table = $('#table'),
                per_page = $('.per-page');
     
            // default state for page
            var state = {
                page: 1,
                per_page: per_page.val(),
                columns: [],
                ordering: []
            };

            var rnd = {
                tablerows: new renderer.template({
                    target: table,
                    template: templates.row
                })
            };

            var src = {
                tablerows: new datasource.ajax({
                    uri: report.attr('data-uri'),
                    success: function(json) {
                        rnd.tablerows.render(json);
                    }
                })
            };

            src.tablerows.get();
            
            /*
             * Hook up the elements that change the number of rows per page.
             */
            var pb;
            report.delegate('.per-page', 'change', function(evt) {
                pb = this.value;
                state.per_page = pb;
                report.trigger('update.report', {'per_page': pb});
                return false;
            });
            
            /*
             * Hook up the elements that change the page.
             */
            var p;
            report.delegate('.page', 'click', function(evt) {
                p = this.innerHTML;
                state.page = p;
                report.trigger('update.report', {'page': this.innerHTML});
                return false;
            });
            
            /*
             * Define primary event that handles fetching data.
             */
            var uri = report.attr('data-uri');
            report.bind('update.report', function(evt, params) {
                src.tablerows.get(params);
                console.log(state);
                return false;
            });
        });
    });
