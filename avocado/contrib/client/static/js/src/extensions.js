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

    $.log = function(msg) {
        /*
        ** Simple helper to either log to console (gecko or webkit) otherwise
        ** display an alert.
        */
        if (window.console)
            console.log(msg);
        else
            alert(msg);
    };
    
    $.jqoteobj = function(template, data, tag) {
        /*
        ** Wraps the default $.jqote result in a jQuery object.
        */
        return $($.jqote(template, data, tag));
    };

    $.fn.placeholder = function(text) {
        /*
        ** Provides a simple means for having inline "help text" for text input
        ** fields. This currently only applies to input[type=text] or textarea
        ** fields. The behavior allows for displaying `text' in grey
        ** on blur and is hidden on focus.
        */
        var obj = this;

        obj.each(function() {
            var $this = $(this);
            text = text || $this.attr('placeholder');

            if (!$this.is('input') && !$this.is('textarea'))
                return obj;

            // set initial style
            if (this.value == '' || this.value == text) {
                $this.val(text).css('color', '#999');
            } else {
                $this.css('color', '#000');
            }
            
            // bind events
            $this.focus(function() {
                $this.css('color', '#000');
                if ($this.val() == text) {
                    $this.val('');
                }
            }).blur(function() {
                $this.css('color', '#000');
                if ($this.val() == '') {
                    $this.val(text).css('color', '#999');
                }
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

    $.fn.autocomplete = function(ajax, placeholder, timeout, single) {
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
        ** `timeout' - defines the amount of time between each keyup before
        ** triggering a request. Default is 400.
        **
        ** `single' - if true will only hit the server the first time and store
        ** the response locally. successive requests will use the response and
        ** will not hit the server. Default is false.
        */
        if (!this.is('input[type=text]') && !this.is('input[type=search]'))
            throw new TypeError('A text or search field is required');            

        return this.each(function() {
            placeholder = placeholder || null;
            timeout = timeout || 300;
            single = single || false;

            var $input = $(this),
                $form,
                query,
                ajax_,                
                last = null,
                timer = null,
                first = null,
                done = true;
            
            // setup defaults
            ajax.success = ajax.success || function(){};
            ajax.error = ajax.error || function(){};
            ajax.start = ajax.start || function(){};
            ajax.end = ajax.end || function(){};
            ajax.data = ajax.data || {q: query};
            
            ajax_ = $.extend('deep', {}, ajax);
        
            // prevent form submission (e.g. via the Enter key)
            $form = $input.closest('form').submit(function(evt) {
                evt.preventDefault();
                evt.stopPropagation();
            });
            
            ajax_.url = $form.attr('action');

            // redefine the `success' to provide additional argument
            ajax_.success = function(resp, status, xhr) {
                // process user-defined ajax-success handler
                ajax.success(query, resp, status, xhr);
                // if only a single request is to be made, cache first response
                // for later faux-usage
                if (first == null && single)
                    first = {resp: resp, status: status, xhr: xhr};
                last = query;
                done = true;
                ajax_.end();
            };
        
            ajax_.error = function(xhr, status, err) {
                ajax.error(query, xhr, status, err);
                ajax_.end();
            };
            
            ajax_.start = function() {
                done = false;
                ajax.start(query);
            };
            
            ajax_.end = function() {
                done = true;
                ajax.end();
            };
            
            $input.keyup(function() {
                // clear previous timeout to cancel last request
                clearTimeout(timer);

                // get new value
                query = $input.val();

                // if any `placeholder' is provided, test if the value matches it
                if (placeholder != null && query == placeholder)
                    query = '';

                // sanitize and strip useless stopwords
                // temporary commenting out, have to find the file its in JMM
                // query = SearchSanitizer.clean(query);
                
                if (query != last) {
                    // only start once, when the user first begins typing
                    if (done == true)
                        ajax_.start();

                    ajax_.data.q = query;

                    timer = setTimeout(function() {
                        // run pseudo-request for single request autocompletes
                        if (single && first)
                            ajax_.success(first.resp, first.status, first.xhr);
                        else
                            $.ajax(ajax_);
                    }, timeout);
                } else {
                    ajax_.end();
                }
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
