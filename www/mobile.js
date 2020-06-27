var mobile;

PSM = (function(window, document, $) {

    'use strict';

    var self;
    var favourites_visible = false;
    var search_visible = false;
    var loading = 0;
    var favourite_card_ids = [];

    var construct = function() {
        self = this;
        self.init();
    };

    function init() {

        // events
        $('body').on('click', '#show-favourites', self.toggle_favourites);
        $('body').on('click', '#globe', self.toggle_search);
        $('body').on('keyup', '#search', self.trigger_search);
        $('body').on('click', '#search button', self.trigger_search);
        $('body').on('click', '#marbles .marble', self.load_card_modal);
        $('body').on('click', '#favourites .favourite', self.load_card_modal);
        $('body').on('click', '.modal .tag', self.add_favourite);

        // calls
        self.flush_favourites();
        self.flush_search();
        self.flush_marbles();
        self.flush_card_modal();
        self.info();
        self.search();
        self.load_favourites();

    };

    function toggle_favourites() {
        if(favourites_visible) {
            $('#favourites').hide();
            favourites_visible = false;
        } else {
            self.load_favourites();
            $('#favourites').show();
            favourites_visible = true;
        }
    };

    function toggle_search() {
        if(search_visible) {
            $('#search').hide();
            search_visible = false;
            $('#globe, #marbles').css('opacity', 1);
        } else {
            $('#search').show();
            search_visible = true;
            $('#globe, #marbles').css('opacity', 0.25);
        }
    };

    function trigger_search(event) {
        if(typeof event.keyCode == 'undefined' || event.keyCode == 13) {
            $('#search').hide();
            search_visible = false;
            $('#globe, #marbles').css('opacity', 1);
            self.search();
        }
    };

    function search(card_id=null) {
        self.flush_marbles();
        if(card_id != null) {
            var getUrl = 'http://localhost:1352/?function=Search&query=' + encodeURIComponent(card_id);
        } else {
            var keywords = $('#keywords').val();
            var getUrl = 'http://localhost:1352/?function=Search&query=' + encodeURIComponent(keywords);
        }
        self.request(getUrl, function(items) {
            if(typeof items[0].cards != 'undefined') {
                var cards = items[0].cards;
                for(var i in cards) {
                    var card = cards[i];
                    self.render_marble(i, card);
                }
            }
        });
    };

    function start_loading() {
        $('#globe').addClass('loading');
        loading++;
    };

    function finish_loading() {
        loading--;
        if(loading == 0) {
            $('#globe').removeClass('loading');
        }
    };

    function render_marble(i, card) {
        var marble_number = parseInt(i) + 1;
        if(marble_number <= 8) {

            var source_logo = '';
            var $marble = $('#marbles .marble:nth-child(' + marble_number + ')');

            $marble.attr('data-card-id', card['id']);

            if(card['shout_outs'] > 0) {
                $marble.addClass('shouted');
            } else {
                $marble.removeClass('shouted');
            }
            if(card['type'] == 'fact') {
                $marble.removeClass('idea');
                $marble.addClass('fact');
            } else {
                $marble.removeClass('fact');
                $marble.addClass('idea');
            }
            if(card['relation_type'] == 'confluence' && card['type'] == 'idea') {
                source_logo = 'image/confluence-logo.png';
            } else if(card['relation_type'] == 'jira' && card['type'] == 'idea') {
                source_logo = 'image/jira4.png';
            } else if(card['relation_type'] == 'git' && card['type'] == 'idea') {
                source_logo = 'image/GitLab_Logo.png';
            } else {
                source_logo = 'image/phoenix_logo.png';
            }
            $('img.logo', $marble).attr('src', source_logo);
            $marble.removeClass('off');
            $marble.addClass('on');

        }
    };

    function flush_marbles() {
        var $marbles = $('#marbles .marble');
        $marbles.removeClass('fact');
        $marbles.removeClass('on');
        $marbles.removeClass('shouted');
        $marbles.addClass('idea');
        $marbles.addClass('off');
        $marbles.attr('data-card-id', 0);
        $('img.logo', $marbles).attr('src', 'image/phoenix_logo.png');
    };

    function info() {
        var getUrl = 'http://localhost:1352/?function=Ping';
        self.request(getUrl, function(items) {
            if(typeof items[0].idea_count != 'undefined' && typeof items[0].fact_count != 'undefined') {
                $('#keywords').attr('placeholder', '');
                var total_count = items[0].idea_count + items[0].fact_count;
                $('#keywords').attr('placeholder', "Suche in " + total_count + " Fakten und Ideen");
                if(total_count <= 0) {
                    $('#globe p').text('<i class="fas fa-exclamation-triangle"></i>');
                } else {
                    $('#globe p').text(total_count);
                }
            }
        });
    };

    function load_card_modal(event) {
        var card_id = $(event.currentTarget).attr('data-card-id');
        if(card_id > 0) {
            self.track_click(card_id);

            var getUrl = 'http://localhost:1352/?function=Search&query=' + encodeURIComponent(card_id);
            self.request(getUrl, function(items) {
                if(typeof items[0].cards != 'undefined') {
                    var cards = items[0].cards;
                    if(cards.length > 0) {
                        var card = cards[0];
                        self.render_card_modal(card);
                    } else {
                        console.log('Error - card with id ' + card_id + ' could not be loaded');
                    }
                }
            });

        }
    };

    function render_card_modal(card) {
        var is_favourite = favourite_card_ids.indexOf(card['id']) > -1;
        var $modal = $('#detail');
        $('.tag', $modal).attr('data-card-id', card['id']);
        $('[name=card_id]', $modal).val(card['id']);
        $('.title', $modal).text(card['title']);
        $('.text', $modal).val(card['text']);
        $('.external_link', $modal).text(card['external_link']);
        $('.external_link', $modal).attr('href', card['external_link']);
        if(card['keywords'] != null) {
            $('.keywords', $modal).text(card['keywords'].join(', '));
        } else {
            $('.keywords', $modal).text('');
        }
        if(card['editors'] != null) {
            $('.editors', $modal).text(card['editors'].join(', '));
        } else {
            $('.editors', $modal).text('');
        }
        $('#detail').modal();
        if(is_favourite) {
            $('.far.fa-star', $modal).removeClass('far').addClass('fas');
        } else {
            $('.fas.fa-star', $modal).removeClass('fas').addClass('far');
        }
    };

    function flush_card_modal() {
        var $modal = $('#detail');
        $('.fas.fa-star', $modal).removeClass('fas').addClass('far');
        $('.tag', $modal).attr('data-card-id', 0);
        $('[name=card_id]', $modal).val('');
        $('.title', $modal).text('');
        $('.text', $modal).val('');
        $('.external_link', $modal).text('');
        $('.external_link', $modal).attr('href', '');
        $('.keywords', $modal).text('');
        $('.editors', $modal).text('');
    };

    function track_click(card_id) {
        var query = $('#keywords').val();
        var getUrl = 'http://localhost:1352/?function=Click&card_id=' + encodeURIComponent(card_id) + '&query=' + encodeURIComponent(query) + '&loading_seconds=-1';
        self.request(getUrl);
    };

    function flush_search() {
        $('#search input').val('');
    };

    function load_favourites() {
        var getUrl = 'http://localhost:1352/?function=Favourites';
        self.request(getUrl, function(items) {
            if(typeof items[0].favourites !== 'undefined') {
                self.flush_favourites();
                favourite_card_ids = [];
                for(var i in items[0].favourites) {
                    var favourite = items[0].favourites[i];
                    favourite_card_ids.push(favourite['card_id']);
                    self.render_favourite(favourite);
                }
            }
        });
    };

    function render_favourite(favourite) {
        var $favourite = $('#favourites').append(
            '<p class="favourite" data-card-id="' +
            favourite['card_id'] + '"><i class="fas fa-star"></i> <span class="text">' +
            favourite['card_title'] + '</span></p>'
        );
    };

    function flush_favourites() {
        $('#favourites .favourite').remove();
    };

    function add_favourite(event) {
        var card_id = $(event.currentTarget).attr('data-card-id');
        if(card_id > 0) {
            var getUrl = 'http://localhost:1352/?function=Favourite&card_id=' + card_id;
            self.request(getUrl, function(items) {
                self.load_favourites();
                if(items[0].is_added) {
                    $('#detail .far.fa-star').removeClass('far').addClass('fas');
                } else {
                    $('#detail .fas.fa-star').removeClass('fas').addClass('far');
                }
            });
        }
    };

    function request(url, callback) {
        var formContentType = 'application/x-www-form-urlencoded';
        try {
            var xhr = new XMLHttpRequest();
            xhr.open('GET', url, true);
            xhr.setRequestHeader('Content-type', formContentType);
            self.start_loading();
            xhr.onreadystatechange = function() {
                if(xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200 && xhr.responseText) {
                    self.finish_loading();
                    var result = JSON.parse(xhr.responseText);
                    if(typeof callback == 'function') {
                        callback(result.items);
                    }
                }
            };
            xhr.send();
        } catch(e) {
            console.log(e.message);
        }
    };

    construct.prototype = {
        init: init,
        toggle_favourites: toggle_favourites,
        toggle_search: toggle_search,
        trigger_search: trigger_search,
        search: search,
        start_loading: start_loading,
        finish_loading: finish_loading,
        render_marble: render_marble,
        flush_marbles: flush_marbles,
        info: info,
        load_card_modal: load_card_modal,
        render_card_modal: render_card_modal,
        flush_card_modal: flush_card_modal,
        track_click: track_click,
        flush_search: flush_search,
        request: request,
        load_favourites: load_favourites,
        render_favourite: render_favourite,
        flush_favourites: flush_favourites,
        add_favourite: add_favourite
    };

    return construct;

})(window, document, jQuery);

$(document).ready(function() {
    mobile = new PSM();
});