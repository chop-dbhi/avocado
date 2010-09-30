require.def('rest/datasource', ['rest/basext'], function(BaseExt) {
    
    var DataSource = BaseExt.extend({});

    var AjaxDataSource = DataSource.extend({
        get: function(params) {
            params = params || this.params;

            var self = this;
            this.xhr = $.ajax({
                url: self.uri,
                data: params,
                success: self.success(resp, status, xhr),
                error: self.error(xhr, status, error)
            });
            return this;
        }
    }, {
        defargs: {
            uri: window.location,
            params: {},
            success: function() {},
            error: function() {}
        }
    });

    return {
        ajax: AjaxDataSource
    };
});
