require.def('rest/renderer',['lib/base','lib/jquery.jqote2'],function(){var Renderer=Base.extend({_datamethod:function(data){this.data=data;return function(key,value){if(key===undefined)
return this.data;if(value===undefined)
return this.data[key];this.data[key]=value;};},_bindata:function(e,d){if(e.jquery!==undefined)
e.data(d);else if(typeof e=='object')
e.data=this._datamethod(d);return e;},_defargslist:function(constr,argslist){constr=constr||this.constructor;argslist=argslist||[];if(constr.ancestor)
argslist=this._defargslist(constr.ancestor,argslist);if(constr.defargs&&typeof constr.defargs=='object')
argslist.push(constr.defargs);return argslist;},constructor:function(args){var defargslist=this._defargslist(),defargs=$.extend.apply(this,[{}].concat(defargslist)),cpargs=$.extend({},defargs,args);for(var key in cpargs){if(defargs.hasOwnProperty(key))
this[key]=cpargs[key];}}},{defargs:{target:null}});var TemplateRenderer=Renderer.extend({render:function(data,append){append=typeof append=='boolean'?append:this.append;if(!append)
this.target.html('');for(var d,e,i=0;i<data.length;i++){d=data[i];e=$.jqoteobj(this.template,d);e=this._bindata(e,d);this.target.append(e);}
return this.target;}},{defargs:{template:null,append:false}});return{base:Renderer,template:TemplateRenderer};});