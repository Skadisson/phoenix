var phoenix;

PX = (function(window, document, $) {

    'use strict';

    var self;

    var construct = function() {
        self = this;
        self.init();
    };

    function init() {
        $('input[type=text]').focus();
    };

    function darkmode() {
        $('body').toggleClass('dark');
    };

    construct.prototype = {
        init: init,
        darkmode: darkmode
    };

    return construct;

})(window, document, jQuery);

phoenix = new PX();