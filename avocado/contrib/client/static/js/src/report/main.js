require.def('report/main', ['report/templates', 'lib/jquery.jqote2'], function(templates) {
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
        
        /*
         * Hook up the elements that change the number of rows per page.
         */
        var pb;
        report.delegate('.per-page', 'change', function(evt) {
            pb = this.value;
            if (state.per_page == pb)
                return false;
            per_page.val(pb);
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
            if (state.page == p)
                return false;
            state.page = p;
            report.trigger('update.report', {'page': this.innerHTML});
            return false;
        });
        
        /*
         * Define primary event that handles fetching data.
         */
        var uri = report.attr('data-uri');
        report.bind('update.report', function(evt, data) {
            $.getJSON(uri, data, function(json) {
                /*
                 * the header will not be present if the columns have not changed
                 */
                if (json.header)
                    table.jqotesub(templates.header, json.header);
                table.jqotesub(templates.row, json.data);
            });
        });
    });
});
