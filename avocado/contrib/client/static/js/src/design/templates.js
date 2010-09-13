require.def('design/templates', function() {
    return {
        criteria: {
            list: [
                '<div data-model="criterion" data-uri="<%= this.uri %>" ',
                    'data-search-select data-search-term="<%= this.name.toLowerCase() %>">',
                    '<strong><%= this.name %></strong>',
                    '<p class="ht mg"><%= this.description %></p>',
                '</div>'
            ].join('')
        },
        categories: {
            list: '<span data-model="category" data-search-select ' +
                'data-search-term="<%= this.name.toLowerCase() %>"><%= this.name %></span>'
        }
    };    
});
