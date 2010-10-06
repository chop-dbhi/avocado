// report/main

require(
    
    ['report/table', 'report/search'],

    function(m_table, m_search) {

        $(function() {
            var shared = m_table.init();
            m_search.init(shared);
        });

    }
);
