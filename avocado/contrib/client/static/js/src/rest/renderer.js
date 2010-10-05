// rest/renderer

require.def(
    
    'rest/renderer',
    
    ['rest/basext', 'lib/jquery.jqote2'],
    
    function(BaseExt) {
        /*
         * The base renderer class. A renderer takes data and uses it to act
         * on other objects, whether be DOM elements or other JS objects.
         *
         * @class
         */
        var Renderer = BaseExt.extend({}, {
            defargs: {
                target: null
            }
        });

        var TemplateRenderer = Renderer.extend({
            /*
             * Takes an object or array, `data`, and creates an new DOM element that
             * will be inserted into the `target` object. The DOM element is created
             * from the `template` attribute.
             *
             * @params <string|boolean> replace - can be one of three values
             * including: `true`, 'append' or 'prepend'. This defines the means
             * of insertion into the DOM.
             */
            render: function(data, replace) {
                replace = !!replace ? replace : this.replace;

                if (replace === true)
                    this.target.html('');

                if (this.bindData === true) {
                    l = [];
                    for (var d, e, i = 0; i < data.length; i++) {
                        d = data[i];
                        e = $.jqoteobj(this.template, d);
                        e.data(d);
                        l.push(e);
                    }
                } else {
                    l = [$.jqoteobj(this.template, data)];
                }
         
                var tgt = this.target;
                if (replace === 'prepend')
                    $.each(l.reverse(), function() { tgt.prepend(this); });
                else
                    $.each(l, function() { tgt.append(this); });

                return this.target;
            }
        }, {
            defargs: {
                template: null,
                replace: true,
                bindData: false
            }
        });

        return {
            base: Renderer,
            template: TemplateRenderer
        };
    }
);
