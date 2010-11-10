require.def('html5fix', function() {
    $(function() {
        if (!Modernizr.input.placeholder) {
            $('input[placeholder]').placeholder();
        }
        
        if (!Modernizr.input.autofocus) {
            $('input[autofocus]').focus();
        }
    });    
});
