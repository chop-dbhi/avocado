/*
** Define the default functions to be used with any AJAX requrest.
** Setup the defaults for all AJAX requests.
*/

/*
** Handles HTTP redirects.
*/
$.ajaxSetup({
    complete: function(xhr) {
        if (xhr.status === 302) {
            var json = $.parseJSON(xhr.responseText);
            if (json.redirect)
                window.location = json.redirect;
        }
    }
});

// $.blockUI.defaults.message = null;
// $.blockUI.defaults.css = {};
// $.blockUI.defaults.overlayCSS = {};