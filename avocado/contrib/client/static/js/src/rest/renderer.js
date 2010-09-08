require.def('rest/renderer', ['lib/base', 'lib/jquery.jqote2'], function() {
    /*
     * The base renderer class. A renderer takes data and uses it to act
     * on other objects, whether be DOM elements or other JS objects.
     *
     * @class
     */
    var Renderer = Base.extend({
        /*
         * @param <jQuery object> target The target object that will be acted
         * on with the data.
         */
        _datamethod: function(data) {
            this.data = data;
            return function(key, value) {
                if (key === undefined)
                    return this.data;
                if (value === undefined)
                    return this.data[key];
                this.data[key] = value;
            };
        },

        _bindata: function(e, d) {
            if (e.jquery !== undefined)
                e.data(d);
            else if (typeof e == 'object')
                e.data = this._datamethod(d);
            return e;
        },

        _defargslist: function(constr, argslist) {
            constr = constr || this.constructor;
            argslist = argslist || [];

            // populate ancestor args first
            if (constr.ancestor)
                argslist = this._defargslist(constr.ancestor, argslist);

            if (constr.defargs && typeof constr.defargs == 'object')
                argslist.push(constr.defargs);

            return argslist;
        },
        
        _defargs: function() {
            var defargslist = this._defargslist();
            return $.extend.apply(this, [{}].concat(defargslist));
        },

        constructor: function(args) {
            var defargs = this._defargs(),
                cpargs = $.extend({}, defargs, args);

            // only set attributes that are defined in `defargs'
            for (var key in cpargs) {
                if (defargs.hasOwnProperty(key))
                    this[key] = cpargs[key];
            }
        }
    }, {
        defargs: {
            target: null
        }
    });

    var TemplateRenderer = Renderer.extend({
        render: function(data, append) {
            append = typeof append == 'boolean' ? append : this.append;

            // implied replace
            if (!append)
                this.target.html('');

            for (var d, e, i = 0; i < data.length; i++) {
                d = data[i];
                e = $.jqoteobj(this.template, d);
                e = this._bindata(e, d);
                this.target.append(e);
            }
            return this.target;
        }
    }, {
        defargs: {
            template: null,
            append: false
        }
    });

    return {
        base: Renderer,
        template: TemplateRenderer
    };

});
