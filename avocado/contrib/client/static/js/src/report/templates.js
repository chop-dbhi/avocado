require.def('report/templates', ['lib/jquery.jqote2'], function() {
    return {
        header: $.jqotec('<th class="header <%= this.direction %>"><span><%= this.name %></th>'),
        row: $.jqotec([
            '<tr>',
                '<td><input type="checkbox">',
                '<% for(var k=1;k<this.length;k++){ %><td><%= this[k] %></td><% } %>',
            '</tr>'
        ].join(''))
    };
}); 
