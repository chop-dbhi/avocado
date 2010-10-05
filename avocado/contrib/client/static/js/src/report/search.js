// report/search

require.def(
    
    'report/search',

    ['rest/datasource', 'rest/renderer', 'report/templates', 'lib/jquery.ui'],

    function(m_datasource, m_renderer, m_templates) {

        function init() {

            var columns = $('#columns'),
                active_columns = $('#active-columns'),

                searchdialog = $('#search-dialog'),
                searchinput = $('#search'),
                searchform = $('form', searchdialog),
                searchbutton = $('#search-button');

            /*
            ** initialize renderers for the available criterion options
            ** and the categories.
            */
            var rnd = {
                columns: new m_renderer.template({
                    target: columns,
                    template: m_templates.columns
                })
            };

            var src = {
                columns: new m_datasource.ajax({
                    uri: searchform.attr('action'),
                    success: function(json) {
                        rnd.columns.render(json);
                    }
                })
            };

            src.columns.get();

            searchinput.autocomplete({
                success: function(value, json) {
                    var objs = $('[data-model=column]', columns);
                    for (var i = 0; i < json.length; i++) {
                        objs.jdata('id', json[i]).addClass('inview');
                    }

//                    rnd.criteria.target.html('<em class="ca mg">no results found for term "'+ value +'"</em>');
                }
            });

            searchdialog.bind('search', function(evt, value) {
                searchinput.trigger('search', value);
                return false;
            });

            searchdialog.dialog({
                autoOpen: false,
                draggable: true,
                resizable: true,
                title: 'Show/Hide Columns',
                height: 550,
                width: 700,
                minWidth: 700,
                buttons: {
                    Cancel: function() {
                        searchdialog.dialog('close');
                    },
                    Save: function() {
                        var cls,
                        data = {},
                        colIds = $('li:not(.inactive)', $selColumnList).map(function() {
                        cls = this.className.match(/col\d+/)[0];
                        return cls.substr(3);
                        }).get();
                        data = 'column_ids=' + colIds.join(',');
                        refreshRows(window.location.path, 'GET', data);
                        $columnEditor.dialog('close');
                    }
                }
            });

            searchbutton.bind('click', function(evt) {
                searchdialog.dialog('open');
            });
        };

        return {init: init};
    });
//            var $columnSections = $('#column-div .column-section'),
//                $selColumnDiv = $('#sel-column-div'),
//                $selColumnList = $('#sel-column-list').sortable({
//                    placeholder: 'placeholder',
//                    forcePlaceholderSize: true,
//                    forceHelperSize: true,
//                    cursor: 'move',
//                    tolerance: 'intersect'
//                }).disableSelection(),
//
//
//                $columnSearchQ = $('#column-search-q').keyup(function() {  
//                    var q = SearchSanitizer.clean($columnSearchQ.val());
//
//                    clearTimeout($columnSearchQ.attr('timer'));
//
//                    if (q !== $columnSearchQ.attr('lastQ')) {
//                        $columnSearchQ.attr('timer', setTimeout(function() {
//                            $columnSearch.submit();
//                            $columnSearchQ.attr('lastQ', q);
//                        }, 500));
//                    }
//                }).
//
//                $columnSearch = $('#column-search').submit(function(evt) {
//                    evt.preventDefault();
//                    var q = $.trim($columnSearchQ.val().replace(/\s+/, ' ')),
//                        data = {'q': q == 'Search columns...' ? '' : q};
//
//                    $.get(this.action, $.param(data), function(json) {
//                        ajaxSuccess(json);
//                        var classes = json.column_ids.map(function(e) {
//                                return '.col' + e;
//                            }),
//                            classesStr = classes.join(','),
//                            $children = $columnSections.children();
//
//                        if (classes.length == 0) {
//                            $children.addClass('filtered');
//                        } else {                
//                            $children.not(classesStr).addClass('filtered');
//                            $children.filter(classesStr).removeClass('filtered');
//                        }
//
//                        for (var i = $columnSections.length; i--; ) {
//                            var $s = $($columnSections[i]),
//                                len = $s.children().not('.filtered, .inactive').length;
//
//                            if (len == 0) {
//                                $s.parent().addClass('hd');
//                            } else {
//                                $s.parent().removeClass('hd');
//                            }
//                        }
//                    });
//                }).submit();
//
//            ColumnManager = {
//                _aCache: {},
//                _yCache: {},
//                _groupCounts: (function() {
//                    var counts = {}, section, length;
//                    for (var i = $columnSections.length; i--; ) {
//                        section = $($columnSections[i]);
//                        length = section.children().not('.inactive').length;
//                        counts[section.attr('id')] = length;
//                    }
//                    return counts;
//                })(),
//                isPinned: null,
//                reCol: /col(\d+)/,
//            
//                getClass: function(className) {
//                    return '.'+className.match(this.reCol)[0];
//                },
//            
//                getObjs: function(cls) {
//                    var aObj = this._aCache[cls],
//                        yObj = this._yCache[cls];
//
//                    if (aObj === undefined) {
//                        aObj = $(cls, $columnSections);
//                        this._aCache[cls] = aObj;
//                    }
//                
//                    if (yObj === undefined) {
//                        yObj = $(cls, $selColumnList);
//                        this._yCache[cls] = yObj;
//                    }
//                
//                    return [aObj, yObj];
//                },
//            
//                setPinning: function() {
//                    var modalHeight = $columnEditor.height(),
//                        columnDivHeight = $selColumnDiv.height();
//                
//                    if (columnDivHeight > modalHeight) {
//                        if (this.isPinned === false)
//                            return;
//                            
//                        $selColumnDiv.removeClass('pinned');
//                        this.isPinned = false;
//                        // $columnEditor.bind('scroll', columnEditorScrollBind);
//                        // var scrollTop = $columnEditor.scrollTop();
//                        // $selColumnDiv.css('margin-top', scrollTop);
//                    } else {
//                        if (this.isPinned === true)
//                            return;
//                        $selColumnDiv.addClass('pinned');
//                        this.isPinned = true;
//                        // $columnEditor.unbind('scroll');
//                    }
//                },
//                
//                add: function(className) {
//                    /*
//                    ** Handles adding a column to the selected column list.
//                    */
//                    className = className || '';
//
//                    var cls = this.getClass(className),
//                        objSet = this.getObjs(cls),
//                        aObj = objSet[0],
//                        yObj = objSet[1];
//
//                    aObj.addClass('inactive');
//
//                    yObj.detach().removeClass('inactive')
//                        .appendTo($selColumnList);
//                
//                    if (this.isPinned)
//                        this.setPinning();
//                    
//                    var parent = aObj.parent(),
//                        gparent = parent.parent();
//
//                    if (--this._groupCounts[parent.attr('id')] == 0 && !gparent.hasClass('hd'))
//                        gparent.addClass('hd');        },
//            
//                addMany: function(classNames) {
//                    classNames = classNames || [];
//                
//                    for (var cls, i = 0, len = classNames.length; i < len; i++)
//                        this.add(classNames[i]);
//                },
//            
//                remove: function(className) {
//                    /*
//                    ** Handles removing a column from the selected column list.
//                    */
//                    className = className || '';
//
//                    var cls = this.getClass(className),
//                        objSet = this.getObjs(cls),
//                        aObj = objSet[0],
//                        yObj = objSet[1];
//
//                    aObj.removeClass('inactive');
//                    yObj.addClass('inactive');            
//
//                    if (!this.isPinned)
//                        this.setPinning();
//
//                    var parent = aObj.parent(),
//                        gparent = parent.parent();
//
//                    if (++this._groupCounts[parent.attr('id')] > 0 && gparent.hasClass('hd'))
//                        gparent.removeClass('hd');
//                    
//                },
//            
//                removeMany: function(classNames) {
//                    classNames = classNames || [];
//                
//                    for (var i = 0, len = classNames.length; i < len; i++)
//                        this.remove(classNames[i]);
//                }
//            };
//
//
//            // set initial pinning based on loaded columns
//            
//
//            $('.add-category').click(function(evt) {
//                evt.preventDefault();
//                // this does not add filtered out columns 
//                var classNames = [],
//                    items = $(this.hash).children().not('.filtered, .inactive');
//
//                // early exit
//                if (items.length == 0)
//                    return;
//
//                for (var i = 0, len = items.length; i < len; i++)
//                    classNames.push(items[i].className);
//
//                ColumnManager.addMany(classNames);
//            });
//
//
//            $('.add-column').click(function(evt) {
//                evt.preventDefault();
//                ColumnManager.add($(this).parent().attr('className'));
//            });
//
//            $('.remove-column').click(function(evt) {
//                evt.preventDefault();
//                ColumnManager.remove($(this).parent().attr('className'));
//            });
//
//            $('#remove-all').click(function(evt) {
//                evt.preventDefault();
//                var classNames = [],
//                    items = $selColumnList.children().not('.inactive, .locked');
//
//                // early exit
//                if (items.length == 0)
//                    return;
//
//                for (var i = 0, len = items.length; i < len; i++)
//                    classNames.push(items[i].className);
//
//                ColumnManager.removeMany(classNames);        
//            });
//         
//            $('.open-column-editor').click(function(evt) {
//                evt.preventDefault();
//                evt.stopPropagation();
//                $columnEditor.dialog('open');
//                if (ColumnManager.isPinned === null)
//                    ColumnManager.setPinning();
//            });
//
//        };
