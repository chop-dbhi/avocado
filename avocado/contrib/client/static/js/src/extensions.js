/*
** Javascript prototype extensions to the language that may not be present
** across browsers. Before any alterations, a check is done to ensure the
** object method does NOT already exist.
*/

if (!Array.prototype.map) {
    /*
    ** Versions of Javascript pre-1.6 may not include the Array.map
    ** function since it was not part of the ECMA-262 standard.
    */
    Array.prototype.map = function(fun /*, thisp*/) {
        var len = this.length >>> 0;
        if (typeof fun != 'function')
            throw new TypeError();

        var res = new Array(len);
        var thisp = arguments[1];
        for (var i = 0; i < len; i++) {
            if (i in this) {
                res[i] = fun.call(thisp, this[i], i, this);
            }
        }
        return res;
    };
}

/*
** jQuery extensions
*/

(function($) {

    $.extend({
        putJSON: function(url, data, callback, type) {
            return $.ajax({
                type: 'PUT',
                url: url,
                contentType: 'application/json',
                data: data,
                success: callback,
                dataType: type
            });
        },
        
        postJSON: function(url, data, callback, type) {
            return $.ajax({
                type: 'POST',
                url: url,
                contentType: 'application/json',
                data: data,
                success: callback,
                dataType: type
            });
        },
        
        log: function(msg) {
            /*
            ** Simple helper to either log to console (gecko or webkit) otherwise
            ** display an alert.
            */
            if (window.console)
                console.log(msg);
            else
                alert(msg);
        },
    
        jqoteobj: function(template, data, tag) {
            /*
            ** Wraps the default $.jqote result in a jQuery object.
            */
            out = $.jqote(template, data, tag);
            return $(out);
        }
    });

    $.fn.placeholder = function(placeholder) {
        /*
        ** Provides a simple means for having inline "help placeholder" for text input
        ** fields. This currently only applies to input[type=text] or textarea
        ** fields. The behavior allows for displaying `placeholder' in grey
        ** on blur and is hidden on focus.
        */
        var obj = this;

        obj.each(function() {
            var $this = $(this),
                color = $this.css('color');
            placeholder = placeholder || $this.attr('placeholder');

            if (!$this.is('input') && !$this.is('textarea'))
                return obj;

            // set initial style
            if ($this.val()=== '' || $this.val() === placeholder)
                $this.val(placeholder).css('color', '#999');
            
            // bind events
            $this.focus(function() {
                if ($this.val() === placeholder)
                    $this.css('color', color).val('');
            }).blur(function() {
                $this.css('color', color);
                if ($this.val() === '')
                    $this.css('color', '#999').val(placeholder);
            });
        });
        
        return this;
    };

    $.fn.jdata = function(key, value) {
        /*
        ** Filters an array of elements for the given `key' by the given
        ** `value' and returns a jQuery object. 
        */ 
        var arr = $.grep(this, function(e) {
            return ($(e).data(key) == value);
        });
        return $(arr);
    };

    $.fn.autocomplete2 = function(ajax, placeholder, maxTimeout, cacheResp) {
        /*
        ** Binds an input[type=text] field with autocomplete-like behavior.
        ** The parameter `ajax' is required and consists of the
        ** available ajax options defined for $.ajaxSetup(). An additional
        ** parameter (first position) is passed to the `success()' and
        ** `error()' callbacks which is the cleaned query string used for the
        ** request. The following additional options can be specified:
        **
        **      `start' - a function handler to be called when the request has
        **      started
        **
        **      `end' - a function handler to be called after success or error
        **
        ** `maxTimeout' - defines the amount of time between each keyup before
        ** triggering a request. Default is 400.
        **
        ** `cacheResp' - if true will only hit the server the first time and store
        ** the response locally. successive requests will use the response and
        ** will not hit the server. Default is false.
        */
        if (!this.is('input[type=text]') && !this.is('input[type=search]'))
            throw new TypeError('A text or search field is required');            

        placeholder = placeholder || null;
        maxTimeout = maxTimeout || 300;
        cacheResp = cacheResp || false;

        // make copy, so original object is not changed
        var ajaxargs = $.extend({}, ajax);
        
        // setup defaults
        var success = ajaxargs.success || function(){},
            error = ajaxargs.error || function(){},
            start = ajaxargs.start || function(){},
            end = ajaxargs.end || function(){};

        ajaxargs.data = {};
        
        return this.each(function(i) {

            var input = $(this),
                form,
                value,
                cache,
                lastValue = null,
                timer = null,
                firstResp = null,
                loading = false;                

            // prevent default form submission (e.g. via the Enter key)
            form = input.closest('form').submit(function(evt) {return false;});
            ajaxargs.url = form.attr('action');

            // redefine the `success' to provide additional argument
            ajaxargs.success = function(resp, status, xhr) {
                // process user-defined ajax-success handler
                success(value, resp, status, xhr);
                // if only a cacheResp request is to be made, cache first response
                // for later faux-usage
                if (firstResp == null && cacheResp)
                    firstResp = {resp: resp, status: status, xhr: xhr};

                if (cache && status == 'success')
                    input.cache[value] = resp;

                lastValue = value;
                loading = false;
                ajaxargs.end();
            };
        
            ajaxargs.error = function(xhr, status, err) {
                error(value, xhr, status, err);
                ajaxargs.end();
            };
            
            ajaxargs.start = function() {
                loading = true;
                start(value);
            };
            
            ajaxargs.end = function() {
                loading = false;
                end();
            };

            var eventName = 'search-' + i;
            
            input.cache = {};
            input.bind(eventName, function(evt, value_, cache_) {
                cache = cache_ ? true : false;
                value = value_;

                // check to see if in cache
                if (cache && input.cache[value]) {
                    ajaxargs.success(input.cache[value], 'cached', null);
                    return;
                }
                
                // clear previous maxTimeout to cancel last request
                clearTimeout(timer);

                // if any `placeholder' is provided, test if the value matches it
                if (placeholder !== null && value === placeholder)
                    value = '';

                // sanitize and strip useless stopwords and non-alphanumerics, and lowercase
                value = SearchSanitizer.clean(value).toLowerCase();
                
                if (value !== lastValue) {
                    // only start once, when the user first begins typing
                    if (loading == false)
                        ajaxargs.start();

                    ajaxargs.data.q = value;

                    timer = setTimeout(function() {
                        // run pseudo-request for cacheResp request autocompletes
                        if (cacheResp && firstResp)
                            ajaxargs.success(firstResp.resp, firstResp.status, firstResp.xhr);
                        // otherwise, actually make request
                        else
                            $.ajax(ajaxargs);
                    }, maxTimeout);
                } else {
                    // run `end' function which mimics finalizing a duplicate request
                    ajaxargs.end();
                }
            });

            input.keyup(function(evt) {
                input.trigger(eventName, [this.value]);
                return false;
            });
        });
    };
    
    
    $.fn.tabs = (function() {
        /*
        ** Sets up the behavior for a set of tabs. This does not customize the
        ** styling of the tabs, but rather uses a few classes to classify and
        ** keep track which tab is selected.
        **/
        
        var _private = {
            nextTab: function(obj, index, len, cnt) {
                /*
                ** Determines the next tab `index' that is not disabled. Returns
                ** undefined otherwise.
                */
                index = (index === undefined) ? obj.data('tabindex') : index;
                len = len || obj.attr('children').length;
                cnt = (cnt === undefined) ? 0 : cnt+1;

                // all tabs have been tried, stop recursion
                if (cnt == len)
                    return null;
                // test if we are at the end of the list, start at the beginning
                if (len + 1 <= index)
                    return this.nextTab(obj, 0, len, cnt);
                // valid index, test for disabled
                if (obj.children(':nth('+index+')').hasClass('disabled'))
                    return this.nextTab(obj, index+1, len, cnt);
                return index;
            },
            
            getTab: function(obj, index) {
                return obj.children(':nth('+index+')');
            }
        };
        
        var _public = {
            init: function(obj, live, handler) {
                // Here live signifies whether we want to 
                // use the jQuery live feature on the object
                // represented by "this" (which is a jQuery wrapped object)
                obj.data('tabified', true);

                live = (live === true) ? true : false;
                handler = handler || function() {};
            
                var $children = obj.children('.tab');
            
                if (live)
                    $('.tab', obj).live('click', _handler(handler));
                else
                    $children.click(_handler(handler));
            
                // if not are pre-selected, click the first one
                if ($children.filter('.tab-selected').length === 0)
                    $children.not('.disabled').filter(':first').click();                
            },
            
            toggle: function(obj, index) {
                _private.getTab(obj, index).click();
                obj.data('tabindex', index);
            },
            
            disable: function(obj, index) {
                _private.getTab(obj, index).addClass('disabled').removeClass('tab-selected');
                // enable next tab
                nindex = _private.nextTab(obj, index);
                if (nindex !== null)
                    this.toggle(obj, nindex);
            },
            
            enable: function(obj, index) {
                _private.getTab(obj, index).removeClass('disabled');
            }
        };
        
        var _handler = function(handler) {
            return function(evt) {
                evt.preventDefault();
                var $this = $(this).not('.disabled');
                
                if ($this.length == 0 || $this.hasClass('tab-selected'))
                    return false;

                var $siblings = $this.siblings('.tab');
            
                $this.addClass('tab-selected');
                $siblings.removeClass('tab-selected');
                handler(evt, $this);
            };
        };
        
        return function(live, handler) {                                  
            if (typeof live === 'string') {
                // if live is a string, this is not an initiate call, they are accessing
                // a method on the public tabs api, handler will be an index
                if (this.data('tabified') === null)
                    throw new TypeError('tabs have not been initialized yet');
                _public[live](this, handler);
            } else {
                // live is a boolean, we are initiating tabs for the item represented by "this"
                _public.init(this, live, handler);
            }
            return this;
        };
    })();
    
}(jQuery));
