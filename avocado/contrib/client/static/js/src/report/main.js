// report/main

require(
    
    ['report/table', 'report/search'],

    function(m_table, m_search) {

        $(function() {
            $('body').ajaxComplete(function() {
                OVERLAY.fadeOut();
            });

            m_search.init();
            m_table.init();
        });

    }
);
