require.def(
    
    'define/templates',
    
    function() {
        return {           
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
