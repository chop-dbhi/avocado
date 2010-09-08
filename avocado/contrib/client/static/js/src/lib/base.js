/*
Base.js, version 1.1a
Copyright 2006-2010, Dean Edwards
License: http://www.opensource.org/licenses/mit-license.php
*/

var Base=function(){};
Base.extend=function(a,c){var e=Base.prototype.extend;Base._prototyping=true;var d=new this;e.call(d,a);d.base=function(){};delete Base._prototyping;var g=d.constructor,b=d.constructor=function(){if(!Base._prototyping)if(this._constructing||this.constructor==b){this._constructing=true;g.apply(this,arguments);delete this._constructing}else if(arguments[0]!=null)return(arguments[0].extend||e).call(arguments[0],d)};b.ancestor=this;b.extend=this.extend;b.forEach=this.forEach;b.implement=this.implement;
b.prototype=d;b.toString=this.toString;b.valueOf=function(h){return h=="object"?b:g.valueOf()};e.call(b,c);typeof b.init=="function"&&b.init();return b};
Base.prototype={extend:function(a,c){if(arguments.length>1){var e=this[a];if(e&&typeof c=="function"&&(!e.valueOf||e.valueOf()!=c.valueOf())&&/bbaseb/.test(c)){var d=c.valueOf();c=function(){var i=this.base||Base.prototype.base;this.base=e;var j=d.apply(this,arguments);this.base=i;return j};c.valueOf=function(i){return i=="object"?c:d};c.toString=Base.toString}this[a]=c}else if(a){var g=Base.prototype.extend;if(!Base._prototyping&&typeof this!="function")g=this.extend||g;for(var b={toSource:null},
h=["constructor","toString","valueOf"],k=Base._prototyping?0:1;f=h[k++];)a[f]!=b[f]&&g.call(this,f,a[f]);for(var f in a)b[f]||g.call(this,f,a[f])}return this}};
Base=Base.extend({constructor:function(a){this.extend(a)}},{ancestor:Object,version:"1.1",forEach:function(a,c,e){for(var d in a)this.prototype[d]===undefined&&c.call(e,a[d],d,a)},implement:function(){for(var a=0;a<arguments.length;a++)typeof arguments[a]=="function"?arguments[a](this.prototype):this.prototype.extend(arguments[a]);return this},toString:function(){return String(this.valueOf())}});
