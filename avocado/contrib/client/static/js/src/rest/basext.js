require.def('rest/basext', ['lib/base'], function() {
    /*
     * The base renderer class. A renderer takes data and uses it to act
     * on other objects, whether be DOM elements or other JS objects.
     *
     * @class
     */
    var BaseExt = Base.extend({
        /*
         * Recursively builds an array of all ancestors' default arguments.
         * This is intended to mimic the precendence which inheritance provides,
         * but without needing to explicitly define them for each subclass.
         */
        __defargslist: function(constr, argslist) {
            constr = constr || this.constructor;
            argslist = argslist || [];

            // populate ancestor args first
            if (constr.ancestor)
                argslist = this.__defargslist(constr.ancestor, argslist);

            if (constr.defargs && typeof constr.defargs == 'object')
                argslist.push(constr.defargs);

            return argslist;
        },

        /*
         * Builds the array of defaultargs from all ancestors and performs
         * a deepcopy from top to bottom, that is, subclasses take precedence
         * over there parent class when defining a default argument thay
         * already was defined.
         */
        _defargs: function() {
            var defargslist = this.__defargslist();
            return $.extend.apply(this, [{}].concat(defargslist));
        },

        /*
         * Fetches the `defargs` and overrides them with the `args` argument.
         * The 'copied arguments' (`cpargs`) are then applied to the newly
         * constructed instance.
         */
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
        /*
         * The default set of keyword arguments that will be applied to all
         * instances of this class. On construction, any of the default
         * arguments can be overriden. Any arguments that are supplied that
         * do not have a default value will be ignored.
         */
        defargs: {}
    });

    return BaseExt;
});
