require.def(
    
    'design/templates',
    
    function() {
        return {
            criteria: [
                '<div class="inview" data-model="criterion" data-id="<%= this.id %>" data-uri="<%= this.uri %>">',
                    '<span><%= this.name %></span>',
                    '<p class="ht mg hd"><%= this.description %></p>',
                '</div>'
            ].join(''),
            categories: '<span id="tab-<%= this.name.toLowerCase() %>" data-model="category" ' +
                    'data-search-term="<%= this.name.toLowerCase() %>"><%= this.name %></span>',
            
            scope_element: ['<div data-uri="<%=this.uri%>" data-id="<%= this.pk %>" class="criterion clearfix">',
                                '<a href="#" class="remove-criterion">X</a>',
                                '<a href="#" class="field-anchor">',
                                    '<%= this.description %>',
                                '</a>',
                            '</div>'].join(''),
            run_query : '<input id="submit-query" type="button" value="Get Report...">'
        };    
    }
);
