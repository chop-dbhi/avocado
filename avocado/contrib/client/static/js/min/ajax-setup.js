$.ajaxSetup({complete:function(xhr){if(xhr.status===302){var json=$.parseJSON(xhr.responseText);if(json.redirect)
window.location=json.redirect;}}});