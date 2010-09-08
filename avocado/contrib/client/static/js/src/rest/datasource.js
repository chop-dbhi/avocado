require.def('rest/datasource', ['lib/base'], function() {
    
    var DataSource = Base.extend({});

    var AjaxDataSource = DataSource.extend({
        constructor: function(args) {
            // defaults
            var _args = {
                uri: window.location,
                params: {},
                callback: function() {}
            };

            // copy
            args = $.extend({}, _args, args);

            for (var key in args)
                this[key] = args[key];
                
            this.get = function(callback, params, uri) {
                callback = callback || this.callback;
                params = params || this.params;
                uri = uri || this.uri;

                $.get(uri, params, callback);
            }
        }
    }, {
        defargs: {
            uri: window.location,
            params: {},
            start: function() {},
            success: function() {},
            error: function() {},
            stop: function() {}
        }
    });

    return {
        ajax: AjaxDataSource
    };
});
