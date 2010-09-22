require.def('report/main', function() {
    $(function() {
        var report = $('#report'),
            paginate_by = $('.paginate-by');
        
        // default state for page
        var state = {
            page: 1,
            paginate_by: paginate_by.val()
        };
        
        /*
         * Hook up the elements that change the number of rows per page.
         */
        var pb;
        report.delegate('.paginate-by', 'change', function(evt) {
            pb = this.value;
            if (state.paginate_by == pb)
                return false;
            paginate_by.val(pb);
            state.paginate_by = pb;
            report.trigger('update.report', {'paginate_by': pb});
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
                console.log(json);
            });
        });
    });
});