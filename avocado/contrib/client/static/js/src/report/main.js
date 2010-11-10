// report/main

require(
    
    [
        'report/table',
        'report/columns',
        'html5fix',
        'ajaxsetup',
        'extensions',
        'sanitizer'       
    ],

    function(m_table, m_columns) {

        $(function() {
            $('body').ajaxComplete(function() {
                OVERLAY.fadeOut();
            });

            m_columns.init();
            m_table.init();

            var e = $('#export-data');

            e.bind('click', function() {
                e.attr('disabled', true);
                window.location = API_URLS.report + '?f=csv';
                setTimeout(function() {
                    e.attr('disabled', false);
                }, 5000);
                return false;
            });
        });

    }
);
