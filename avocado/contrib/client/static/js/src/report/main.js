require.def('report/main', function() {
    $(function() {
        var report = $('#report'),
            paginate_by = $('.paginate-by');
        
        /*
         * Hook up the elements that change the number of rows per page.
         */
        paginate_by.bind('change', function(evt) {
            paginate_by.val(this.value);
            paginate_by.trigger('update.report', {'paginate_by': this.value});
            return false;
        });
        
        (function() {
            var uri = report.attr('data-uri');
            report.bind('update.report', function(evt, data) {
                $.ajax({
                    type: 'get',
                    url: uri,
                    success: function(json) {
                        console.log(json);
                    }
                });
                return false;
            });
        })();
    });
});