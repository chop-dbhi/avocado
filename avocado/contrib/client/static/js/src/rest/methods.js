require.def('rest', ['lib/jquery.jqote2'], function() {

    /*
     *
     */
    $.fn.databind = function() {




    function Methods() {
        this.cache = {};
    };

    Methods.prototype.GET = function(target, event, template, bindee) {
        /*
         * @param target The DOM selector for the element to be listening for
         * the ``event``.
         *
         * @param event The name of the event to be bound to ``target``.
         *
         * @param template A pre-compiled template or a key for a lookup in
         * ``this.templates``.
         */
        var target = $(target);
            bindee = bindee ? $(bindee) : target;

        bindee.bind(event, function(evt, params, append) {
            evt.stopPropagation();

            if (!data)
                return;

            if (!append)
                target.html('');

            for (var d, e, i = 0; i < data.length; i++) {
                d = data[i];
                e = $($.jqote(template, d)).data(d);
                target.append(e);
            }
        });

        this.cache.GET = {target: target};
    };

    Methods.prototype.init = function(methods) {
        for (var key in methods)
            this[key.toUpperCase()].apply(this, methods[key]);
    };

    return {Methods: Methods};
});
