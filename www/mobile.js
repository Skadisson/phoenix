var mobile;

PSM = (function(window, document, $) {

    'use strict';

    var self;
    var favourites_visible = false;
    var search_visible = false;

    var construct = function() {
        self = this;
        self.init();
    };

    function init() {
        $('body').on('click', '#show-favourites', self.toggle_favourites);
        $('body').on('click', '#globe', self.toggle_search);
    };

    function toggle_favourites() {
        if(favourites_visible) {
            $('#favourites').hide();
            favourites_visible = false;
        } else {
            $('#favourites').show();
            favourites_visible = true;
        }
    };

    function toggle_search() {
        if(search_visible) {
            $('#search').hide();
            search_visible = false;
        } else {
            $('#search').show();
            search_visible = true;
        }
    };

    construct.prototype = {
        init: init,
        toggle_favourites: toggle_favourites,
        toggle_search: toggle_search
    };

    return construct;

})(window, document, jQuery);

$(document).ready(function() {
    mobile = new PSM();
});