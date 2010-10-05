require.def('report/templates', ['lib/jquery.jqote2'], function() {
    return {
        columns: $.jqotec([
            '<div class="category">',
                '<h4><%= this.name %> <a class="ht add-category" href="#<%= this.id %>">Add all</a></h4>',
                '<ul id="cat<%= this.id %>" class="column-section">',
                    '<% for (var e,k=0; k<this.columns.length; k++) { %>',
                        '<% e = this.columns[k]; %>',
                        '<li class="col<%= e.id %>">',
                            '<a class="fr ht add-column" href="#">Add</a>',
                            '<%= e.name %>',
                            '<% if (e.description) { %><p class="ht"><%= e.description %></p><% } %>',
                        '</li>',
                    '<% } %>',
                '</ul>',
            '</div>'
        ].join('')), 

        header: $.jqotec('<th class="header <%= this.direction %>"><span><%= this.name %></span></th>'),

        row: $.jqotec([
            '<tr>',
                '<td><input type="checkbox"></td>',
                '<% for(var k=1; k<this.length; k++) { %>',
                    '<td><%= this[k] %></td>',
                '<% } %>',
            '</tr>'
        ].join('')),

        pages: $.jqotec([
            '<% if (this.page > 1) { %>',
                '<span>&laquo; <a href="#1">First</a></span>',
                '<span>&lsaquo; <a href="#<%= this.page-1 %>">Previous</a></span>',
            '<% } else { %>',
                '<span class="inactive">&laquo; First</span>',
                '<span class="inactive">&lsaquo; Previous</span>',
            '<% } %>',

            '<span class="pages">',
                '<% for (var e,k=0; k<this.pages.length;k++) { %>',
                    '<% e = this.pages[k]; %>',
                    '<% if (this.page == e) { %>',
                        '<strong><%= e %></strong>',
                    '<% } else { %>',
                        '<% if (e) { %>',
                            '<a href="#<%= e %>"><%= e %></a>',
                        '<% } else { %>',
                            '<span>...</span>',
                        '<% } %>',
                    '<% } %>',
                '<% } %>',
            '</span>',

            '<% if (this.page < this.num_pages) { %>',
                '<span><a href="#<%= this.page+1 %>">Next</a> &rsaquo;</span>',
                '<span><a href="#<%= this.num_pages %>">Last</a> (<%= this.num_pages %>) &raquo;</span>',
            '<% } else { %>',
                '<span class="inactive">&rsaquo; Next</span>',
                '<span class="inactive">&raquo; Last</span>',
            '<% } %>'
        
        ].join(''))
    };
}); 
