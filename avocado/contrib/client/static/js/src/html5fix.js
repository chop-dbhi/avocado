require.def('html5fix', ['lib/modernizr'], function() {
    $(function() {
        if (!Modernizr.input.placeholder) {
            $('input[placeholder]').placeholder();
        }
        
        if (!Modernizr.input.autofocus) {
            $('input[autofocus]').focus();
        }
    });    
});
