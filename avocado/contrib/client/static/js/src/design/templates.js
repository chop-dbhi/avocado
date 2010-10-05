require.def('design/templates', function() {
    return {
        criteria: [
            '<div class="inview" data-model="criterion" data-uri="<%= this.uri %>">',
                '<span><%= this.name %></span>',
                '<p class="ht mg hd"><%= this.description %></p>',
            '</div>'
        ].join(''),
        categories: '<span id="tab-<%= this.name.toLowerCase() %>" data-model="category" ' +
                'data-search-term="<%= this.name.toLowerCase() %>"><%= this.name %></span>',
        
        scope_element: ['<div id="<%= this.pk %>" class="criterion clearfix">',
                            '<a href="#" class="remove-criterion">X</a>',
                            '<a href="#" class="field-anchor">',
                            '<%= this.description %>',
                            '</a>',
                        '</div>'].join(''),
        run_query : '<input id="submit-query" type="button" value="Run the query!">'
    };    
});


