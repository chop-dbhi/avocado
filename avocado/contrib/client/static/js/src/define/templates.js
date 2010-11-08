require.def(
    
    'define/templates',
    
    function() {
        return {           
            scope_element: ['<div data-uri="<%=this.uri%>" data-id="<%= this.pk %>" class="criterion clearfix">',
                                '<a href="#" class="remove-criterion"></a>',
                                '<a href="#" class="field-anchor">',
                                    '<%= this.description %>',
                                '</a>',
                            '</div>'].join(''),
            run_query : '<button id="submit-query"><span class="iconic arrow-right"></span> Get Report</button>'
        };    
    }
);
