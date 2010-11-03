/*
 * Sets the default behavior of detecting a temporary redirect and updating the
 * window location. This is mainly useful for session timeouts.
 */

var overlay = $('#overlay');

$('body').bind({
    ajaxComplete: function(evt, xhr, options) {
        if (xhr.status === 302) {
            var json = $.parseJSON(xhr.responseText);
            if (json.redirect)
                window.location = json.redirect;
        }
        overlay.fadeOut('slow');
    },
    ajaxError: function(evt, xhr, options, err) {
        window.location = $('#support-form').attr('href');
    }
});
