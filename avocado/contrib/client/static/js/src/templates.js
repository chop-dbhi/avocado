require.def('templates', ['lib/jquery.jqote2'], function() {
    var templates = {},
        dom = $('#templates').children(),
        len = dom.length;

    for (var t, n, i = 0; i < len; i++) {
        t = $(dom[i]);
        templates[t.attr('data-name')] = $.jqotec(t);
    }
    return templates;
});
