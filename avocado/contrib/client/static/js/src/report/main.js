// report/main

require(
    
    ['report/table', 'report/search'],

    function(m_table, m_search) {

        $(function() {
            m_search.init();
            m_table.init();
        });

    }
);
