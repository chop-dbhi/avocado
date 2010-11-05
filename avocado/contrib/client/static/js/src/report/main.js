// report/main

require(
    
    ['report/table', 'report/columns'],

    function(m_table, m_columns) {

        $(function() {
            $('body').ajaxComplete(function() {
                OVERLAY.fadeOut();
            });

            m_columns.init();
            m_table.init();
        });

    }
);
