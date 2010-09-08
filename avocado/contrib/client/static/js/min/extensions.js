if(!Array.prototype.map){Array.prototype.map=function(fun){var len=this.length>>>0;if(typeof fun!='function')
throw new TypeError();var res=new Array(len);var thisp=arguments[1];for(var i=0;i<len;i++){if(i in this){res[i]=fun.call(thisp,this[i],i,this);}}
return res;};}
(function($){$.log=function(msg){if(window.console)
console.log(msg);else
alert(msg);};$.jqoteobj=function(template,data,tag){return $($.jqote(template,data,tag));};$.fn.placeholder=function(text){var obj=this;obj.each(function(){var $this=$(this);text=text||$this.attr('title');if(!$this.is('input[type=text]')&&!$this.is('textarea'))
return obj;if(this.value==''||this.value==text){$this.val(text).css('color','#999');}else{$this.css('color','#000');}
$this.focus(function(){$this.css('color','#000');if($this.val()==text){$this.val('');}}).blur(function(){$this.css('color','#000');if($this.val()==''){$this.val(text).css('color','#999');}});});return this;};$.fn.jdata=function(key,value){var arr=$.grep(this,function(e){return($(e).data(key)==value);});return $(arr);};$.fn.autocomplete=function(ajax,placeholder,timeout,single){if(!this.is('input[type=text]')&&!this.is('input[type=search]'))
throw new TypeError('A text or search field is required');return this.each(function(){placeholder=placeholder||null;timeout=timeout||300;single=single||false;var $input=$(this),$form,query,ajax_,last=null,timer=null,first=null,done=true;ajax.success=ajax.success||function(){};ajax.error=ajax.error||function(){};ajax.start=ajax.start||function(){};ajax.end=ajax.end||function(){};ajax.data=ajax.data||{q:query};ajax_=$.extend('deep',{},ajax);$form=$input.closest('form').submit(function(evt){evt.preventDefault();evt.stopPropagation();});ajax_.url=$form.attr('action');ajax_.success=function(resp,status,xhr){ajax.success(query,resp,status,xhr);if(first==null&&single)
first={resp:resp,status:status,xhr:xhr};last=query;done=true;ajax_.end();};ajax_.error=function(xhr,status,err){ajax.error(query,xhr,status,err);ajax_.end();};ajax_.start=function(){done=false;ajax.start();};ajax_.end=function(){done=true;ajax.end();};$input.keyup(function(){clearTimeout(timer);query=$input.val();if(placeholder!=null&&query==placeholder)
query='';if(query!=last){if(done==true)
ajax_.start();ajax_.data.q=query;timer=setTimeout(function(){if(single&&first)
ajax_.success(first.resp,first.status,first.xhr);else
$.ajax(ajax_);},timeout);}else{ajax_.end();}});});};$.fn.tabs=(function(){var _private={nextTab:function(obj,index,len,cnt){index=(index===undefined)?obj.data('tabindex'):index;len=len||obj.attr('children').length;cnt=(cnt===undefined)?0:cnt+1;if(cnt==len)
return null;if(len+1<=index)
return this.nextTab(obj,0,len,cnt);if(obj.children(':nth('+index+')').hasClass('disabled'))
return this.nextTab(obj,index+1,len,cnt);return index;},getTab:function(obj,index){return obj.children(':nth('+index+')');}};var _public={init:function(obj,live,handler){obj.data('tabified',true);live=(live===true)?true:false;handler=handler||function(){};var $children=obj.children('.tab');if(live)
$('.tab',obj).live('click',_handler(handler));else
$children.click(_handler(handler));if($children.filter('.tab-selected').length===0)
$children.not('.disabled').filter(':first').click();},toggle:function(obj,index){_private.getTab(obj,index).click();obj.data('tabindex',index);},disable:function(obj,index){_private.getTab(obj,index).addClass('disabled').removeClass('tab-selected');nindex=_private.nextTab(obj,index);if(nindex!==null)
this.toggle(obj,nindex);},enable:function(obj,index){_private.getTab(obj,index).removeClass('disabled');}};var _handler=function(handler){return function(evt){evt.preventDefault();var $this=$(this).not('.disabled');if($this.length==0||$this.hasClass('tab-selected'))
return false;var $siblings=$this.siblings('.tab');$this.addClass('tab-selected');$siblings.removeClass('tab-selected');handler(evt,$this);};};return function(live,handler){if(typeof live==='string'){if(this.data('tabified')===null)
throw new TypeError('tabs have not been initialized yet');_public[live](this,handler);}else{_public.init(this,live,handler);}
return this;};})();}(jQuery));