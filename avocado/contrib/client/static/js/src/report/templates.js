// report/templates

require.def(

    'report/templates',
    
    ['lib/jquery.jqote2'],
    
    function() {
        return {

            columns: $.jqotec([
                '<div data-model="category" data-id="<%= this.id %>">',
                    '<h4><%= this.name %> <a class="ht add-all" href="#<%= this.id %>">Add All</a></h4>',
                    '<ul>',
                        '<% for (var e,k=0; k<this.columns.length; k++) { %>',
                            '<% e = this.columns[k]; %>',
                            '<li class="active" data-model="column" data-id="<%= e.id %>">',
                                '<a class="fr ht add-column" href="#<%= e.id %>">Add</a>',
                                '<%= e.name %>',
                                '<% if (e.description) { %><p class="ht mg"><%= e.description %></p><% } %>',
                            '</li>',
                        '<% } %>',
                    '</ul>',
                '</div>'
            ].join('')), 

            active_columns: $.jqotec([
                '<li data-model="column" data-id="<%= this.id %>">',
                    '<a class="fr ht remove-column" href="#<%= this.id %>">Remove</a>',
                    '<%= this.name %>',
                    '<% if (this.description) { %><p class="ht mg"><%= this.description %></p><% } %>',
                '</li>',
            ].join('')),

            header: $.jqotec('<th data-model="column" data-id="<%= this.id %>" ' +
                'class="header <%= this.direction %>"><span><%= this.name %></span></th>'),

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
                    '<span class="inactive">Next &rsaquo;</span>',
                    '<span class="inactive">Last (<%= this.num_pages %>) &raquo;</span>',
                '<% } %>'
            
            ].join(''))
        };
    }
); 
