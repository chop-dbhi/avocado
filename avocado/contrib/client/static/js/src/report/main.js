require.def('report/main', function() {
    $(function() {
        var report = $('#report'),
            paginate_by = $('.paginate-by');
        
        paginate_by.bind('change', function(evt) {
            paginate_by.val(this.value);
            paginate_by.trigger('update_report', {'paginate_by': this.value});
            return false;
        });
        
        (function() {
            var uri = report.attr('data-uri'),
                sessargs = {};
            report.bind('update_report', function(evt, data) {
                $.ajax({
                    type: 'get',
                    url: uri,
                    success: function(json) {
                        
                    }
                });
                return false;
            });
        })();
    });
});