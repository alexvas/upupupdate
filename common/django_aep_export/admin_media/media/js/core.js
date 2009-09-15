// Core javascript helper functions

// basic browser identification & version
var isOpera = (navigator.userAgent.indexOf("Opera")>=0) && parseFloat(navigator.appVersion);
var isIE = ((document.all) && (!isOpera)) && parseFloat(navigator.appVersion.split("MSIE ")[1].split(";")[0]);

// Cross-browser event handlers.
function addEvent(obj, evType, fn) {
    if (obj.addEventListener) {
        obj.addEventListener(evType, fn, false);
        return true;
    } else if (obj.attachEvent) {
        var r = obj.attachEvent("on" + evType, fn);
        return r;
    } else {
        return false;
    }
}

function removeEvent(obj, evType, fn) {
    if (obj.removeEventListener) {
        obj.removeEventListener(evType, fn, false);
        return true;
    } else if (obj.detachEvent) {
        obj.detachEvent("on" + evType, fn);
        return true;
    } else {
        return false;
    }
}

// quickElement(tagType, parentReference, textInChildNode, [, attribute, attributeValue ...]);
function quickElement() {
    var obj = document.createElement(arguments[0]);
    if (arguments[2] != '' && arguments[2] != null) {
        var textNode = document.createTextNode(arguments[2]);
        obj.appendChild(textNode);
    }
    var len = arguments.length;
    for (var i = 3; i < len; i += 2) {
        obj.setAttribute(arguments[i], arguments[i+1]);
    }
    arguments[1].appendChild(obj);
    return obj;
}

// ----------------------------------------------------------------------------
// Cross-browser xmlhttp object
// from http://jibbering.com/2002/4/httprequest.html
// ----------------------------------------------------------------------------
var xmlhttp;
/*@cc_on @*/
/*@if (@_jscript_version >= 5)
    try {
        xmlhttp = new ActiveXObject("Msxml2.XMLHTTP");
    } catch (e) {
        try {
            xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
        } catch (E) {
            xmlhttp = false;
        }
    }
@else
    xmlhttp = false;
@end @*/
if (!xmlhttp && typeof XMLHttpRequest != 'undefined') {
  xmlhttp = new XMLHttpRequest();
}

// ----------------------------------------------------------------------------
// Find-position functions by PPK
// See http://www.quirksmode.org/js/findpos.html
// ----------------------------------------------------------------------------
function findPosX(obj) {
    var curleft = 0;
    if (obj.offsetParent) {
        while (obj.offsetParent) {
            curleft += obj.offsetLeft - ((isOpera) ? 0 : obj.scrollLeft);
            obj = obj.offsetParent;
        }
        // IE offsetParent does not include the top-level 
        if (isIE && obj.parentElement){
            curleft += obj.offsetLeft - obj.scrollLeft;
        }
    } else if (obj.x) {
        curleft += obj.x;
    }
    return curleft;
}

function findPosY(obj) {
    var curtop = 0;
    if (obj.offsetParent) {
        while (obj.offsetParent) {
            curtop += obj.offsetTop - ((isOpera) ? 0 : obj.scrollTop);
            obj = obj.offsetParent;
        }
        // IE offsetParent does not include the top-level 
        if (isIE && obj.parentElement){
            curtop += obj.offsetTop - obj.scrollTop;
        }
    } else if (obj.y) {
        curtop += obj.y;
    }
    return curtop;
}

//-----------------------------------------------------------------------------
// Date object extensions
// ----------------------------------------------------------------------------
Date.prototype.getCorrectYear = function() {
    // Date.getYear() is unreliable --
    // see http://www.quirksmode.org/js/introdate.html#year
    var y = this.getYear() % 100;
    return (y < 38) ? y + 2000 : y + 1900;
}

Date.prototype.getTwoDigitMonth = function() {
    return (this.getMonth() < 9) ? '0' + (this.getMonth()+1) : (this.getMonth()+1);
}

Date.prototype.getTwoDigitDate = function() {
    return (this.getDate() < 10) ? '0' + this.getDate() : this.getDate();
}

Date.prototype.getTwoDigitHour = function() {
    return (this.getHours() < 10) ? '0' + this.getHours() : this.getHours();
}

Date.prototype.getTwoDigitMinute = function() {
    return (this.getMinutes() < 10) ? '0' + this.getMinutes() : this.getMinutes();
}

Date.prototype.getTwoDigitSecond = function() {
    return (this.getSeconds() < 10) ? '0' + this.getSeconds() : this.getSeconds();
}

Date.prototype.getISODate = function() {
    return this.getCorrectYear() + '-' + this.getTwoDigitMonth() + '-' + this.getTwoDigitDate();
}

Date.prototype.getHourMinute = function() {
    return this.getTwoDigitHour() + ':' + this.getTwoDigitMinute();
}

Date.prototype.getHourMinuteSecond = function() {
    return this.getTwoDigitHour() + ':' + this.getTwoDigitMinute() + ':' + this.getTwoDigitSecond();
}

Date.prototype.format=function(format){var returnStr='';var replace=Date.replaceChars;for(var i=0;i<format.length;i++){var curChar=format.charAt(i);if(replace[curChar]){returnStr+=replace[curChar].call(this);}else{returnStr+=curChar;}}return returnStr;};Date.replaceChars={shortMonths:['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'],longMonths:['January','February','March','April','May','June','July','August','September','October','November','December'],shortDays:['Sun','Mon','Tue','Wed','Thu','Fri','Sat'],longDays:['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'],d:function(){return(this.getDate()<10?'0':'')+this.getDate();},D:function(){return Date.replaceChars.shortDays[this.getDay()];},j:function(){return this.getDate();},l:function(){return Date.replaceChars.longDays[this.getDay()];},N:function(){return this.getDay()+1;},S:function(){return(this.getDate()%10==1&&this.getDate()!=11?'st':(this.getDate()%10==2&&this.getDate()!=12?'nd':(this.getDate()%10==3&&this.getDate()!=13?'rd':'th')));},w:function(){return this.getDay();},z:function(){return"Not Yet Supported";},W:function(){return"Not Yet Supported";},F:function(){return Date.replaceChars.longMonths[this.getMonth()];},m:function(){return(this.getMonth()<11?'0':'')+(this.getMonth()+1);},M:function(){return Date.replaceChars.shortMonths[this.getMonth()];},n:function(){return this.getMonth()+1;},t:function(){return"Not Yet Supported";},L:function(){return"Not Yet Supported";},o:function(){return"Not Supported";},Y:function(){return this.getFullYear();},y:function(){return(''+this.getFullYear()).substr(2);},a:function(){return this.getHours()<12?'am':'pm';},A:function(){return this.getHours()<12?'AM':'PM';},B:function(){return"Not Yet Supported";},g:function(){return this.getHours()%12||12;},G:function(){return this.getHours();},h:function(){return((this.getHours()%12||12)<10?'0':'')+(this.getHours()%12||12);},H:function(){return(this.getHours()<10?'0':'')+this.getHours();},i:function(){return(this.getMinutes()<10?'0':'')+this.getMinutes();},s:function(){return(this.getSeconds()<10?'0':'')+this.getSeconds();},e:function(){return"Not Yet Supported";},I:function(){return"Not Supported";},O:function(){return(this.getTimezoneOffset()<0?'-':'+')+(this.getTimezoneOffset()/60<10?'0':'')+(this.getTimezoneOffset()/60)+'00';},T:function(){return"Not Yet Supported";},Z:function(){return this.getTimezoneOffset()*60;},c:function(){return"Not Yet Supported";},r:function(){return this.toString();},U:function(){return this.getTime()/1000;}};

// ----------------------------------------------------------------------------
// String object extensions
// ----------------------------------------------------------------------------
String.prototype.pad_left = function(pad_length, pad_string) {
    var new_string = this;
    for (var i = 0; new_string.length < pad_length; i++) {
        new_string = pad_string + new_string;
    }
    return new_string;
}

// ----------------------------------------------------------------------------
// Get the computed style for and element
// ----------------------------------------------------------------------------
function getStyle(oElm, strCssRule){
    var strValue = "";
    if(document.defaultView && document.defaultView.getComputedStyle){
        strValue = document.defaultView.getComputedStyle(oElm, "").getPropertyValue(strCssRule);
    }
    else if(oElm.currentStyle){
        strCssRule = strCssRule.replace(/\-(\w)/g, function (strMatch, p1){
            return p1.toUpperCase();
        });
        strValue = oElm.currentStyle[strCssRule];
    }
    return strValue;
}
