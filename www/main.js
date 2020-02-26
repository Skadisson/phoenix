var main;

PS = (function(window, document, $) {

    'use strict';

    var self;
    var loading = 0;

    var construct = function() {
        self = this;
        self.init();
    };

    function init() {
        self.info();
        self.latest_cards();
        self.favourites();

        $('input[type=text]').focus();
        self.register_events();
    };

    function register_events() {
        $('body').off('click');
        $('body').on('click', '.fa-bullseye', self.suggest_keywords);
        $('body').on('click', '.fa-external-link-square-alt', self.open_external_link);
    };

    function start_loading() {
        loading++;
        $('.loading').stop().animate({'opacity': 1}, 200);
    };

    function finish_loading() {
        loading--;
        if(loading == 0) {
            $('.loading').stop().animate({'opacity': 0}, 200);
        }
    };

    function render_notification(text, is_error = false) {
        if(!is_error) {
            var $notification = $('.notification-template').clone();
            $notification.removeClass('notification-template');
            $notification.addClass('notification');
        } else {
            var $notification = $('.error-template').clone();
            $notification.removeClass('error-template');
            $notification.addClass('error');
        }
        $notification.removeClass('hidden');
        $('#log').prepend($notification);
        $('.notification-info', $notification).text(text);
        $notification.animate({'opacity': 1}, 200);
        $notification.animate({'opacity': 0}, 6000, 'swing', function() {
            $notification.remove();
        });
    }

    function suggest_keywords() {
        var $keyword_field = $('[name=keywords]', $(this).parent());
        var title = $('[name=title]', $(this).parent().parent()).val();
        var text = $('[name=text]', $(this).parent().parent()).val();
        self.keywords(title, text, $keyword_field);
    };

    function open_external_link() {
        var external_link = $('[name=external_link]', $(this).parent()).val();
        if(external_link != '') {
            window.open(external_link);
        }
    };

    function info() {
        var getUrl = 'http://localhost:1352/?function=Ping';
        var formContentType = 'application/x-www-form-urlencoded';
        try {
            var xhr = new XMLHttpRequest();
            xhr.open('GET', getUrl, true);
            xhr.setRequestHeader('Content-type', formContentType);
            self.start_loading();
            xhr.onreadystatechange = function() {
                if(xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200 && xhr.responseText) {
                    self.finish_loading();
                    self.render_notification('Info geladen');
                    $('#keywords').attr('placeholder', '');
                    var result = JSON.parse(xhr.responseText);
                    if(typeof result.items[0].idea_count != 'undefined' && typeof result.items[0].fact_count != 'undefined') {
                        $('#keywords').attr('placeholder', "Suche Dein Thema in " + result.items[0].idea_count + " Ideen und " + result.items[0].fact_count + " Fakten");
                    }
                }
            };
            xhr.send();
        } catch(e) {
            self.render_notification('Fehler', true);
            console.log(e.message);
        }
    };

    function favourites() {
        var getUrl = 'http://localhost:1352/?function=Favourites';
        var formContentType = 'application/x-www-form-urlencoded';
        try {
            var xhr = new XMLHttpRequest();
            xhr.open('GET', getUrl, true);
            xhr.setRequestHeader('Content-type', formContentType);
            self.start_loading();
            xhr.onreadystatechange = function() {
                if(xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200 && xhr.responseText) {
                    self.finish_loading();
                    self.render_notification('Favoriten geladen');
                    $('#favourites').html('');
                    var result = JSON.parse(xhr.responseText);
                    if(result.items.length > 0 && typeof result.items[0].favourites != 'undefined') {
                        var favourites = result.items[0].favourites;
                        for(var i in favourites) {
                            var favourite = favourites[i];
                            self.render_favourite(favourite);
                        }
                    }
                }
            };
            xhr.send();
        } catch(e) {
            self.render_notification('Fehler', true);
            console.log(e.message);
        }
    };

    function is_favourite_toggled(card_id) {
        return $('.favourite[data-card-id=' + card_id + ']').length > 0;
    };

    function toggle_favourite(card_id) {
        var getUrl = 'http://localhost:1352/?function=Favourite&card_id=' + card_id;
        var formContentType = 'application/x-www-form-urlencoded';
        try {
            var xhr = new XMLHttpRequest();
            xhr.open('GET', getUrl, true);
            xhr.setRequestHeader('Content-type', formContentType);
            self.start_loading();
            xhr.onreadystatechange = function() {
                if(xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200 && xhr.responseText) {
                    self.finish_loading();
                    self.render_notification('Favoriten aktualisiert');
                    var result = JSON.parse(xhr.responseText);
                    if(result.items.length > 0 && typeof result.items[0].favourite != 'undefined' && typeof result.items[0].is_added != 'undefined') {
                        self.favourites();
                        if(result.items[0].is_added) {
                            $('#detail .far.fa-star').removeClass('far').addClass('fas');
                        } else {
                            $('#detail .fas.fa-star').removeClass('fas').addClass('far');
                        }
                    }
                }
            };
            xhr.send();
        } catch(e) {
            self.render_notification('Fehler', true);
            console.log(e.message);
        }

    };

    function latest_cards() {
        var getUrl = 'http://localhost:1352/?function=Latest';
        var formContentType = 'application/x-www-form-urlencoded';
        try {
            var xhr = new XMLHttpRequest();
            xhr.open('GET', getUrl, true);
            xhr.setRequestHeader('Content-type', formContentType);
            self.start_loading();
            xhr.onreadystatechange = function() {
                if(xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200 && xhr.responseText) {
                    self.finish_loading();
                    self.render_notification('Karten geladen');
                    $('#link-list').html('');
                    var result = JSON.parse(xhr.responseText);
                    if(typeof result.items[0].cards != 'undefined') {
                        var cards = result.items[0].cards;
                        for(var i in cards) {
                            var card = cards[i];
                            self.render_card(card);
                        }
                    }
                }
            };
            xhr.send();
        } catch(e) {
            self.render_notification('Fehler', true);
            console.log(e.message);
        }
    };

    function keywords(title, text, $keyword_field) {
        var getUrl = 'http://localhost:1352/?function=Keywords&title=' + encodeURIComponent(title) + '&text=' + encodeURIComponent(text);
        var formContentType = 'application/x-www-form-urlencoded';
        try {
            var xhr = new XMLHttpRequest();
            xhr.open('GET', getUrl, true);
            xhr.setRequestHeader('Content-type', formContentType);
            self.start_loading();
            xhr.onreadystatechange = function() {
                if(xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200 && xhr.responseText) {
                    self.finish_loading();
                    self.render_notification('Keywords vorgeschlagen');
                    var result = JSON.parse(xhr.responseText);
                    if(typeof result.items[0].suggested_keywords != 'undefined') {
                        $keyword_field.val(result.items[0].suggested_keywords);
                    }
                }
            };
            xhr.send();
        } catch(e) {
            self.render_notification('Fehler', true);
            console.log(e.message);
        }
    };

    function search(card_id=null) {
        if(card_id != null) {
            var getUrl = 'http://localhost:1352/?function=Search&query=' + encodeURIComponent(card_id);
        } else {
            var keywords = $('#keywords').val();
            var getUrl = 'http://localhost:1352/?function=Search&query=' + encodeURIComponent(keywords);
        }
        var formContentType = 'application/x-www-form-urlencoded';
        try {
            var xhr = new XMLHttpRequest();
            xhr.open('GET', getUrl, true);
            xhr.setRequestHeader('Content-type', formContentType);
            self.start_loading();
            xhr.onreadystatechange = function() {
                if(xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200 && xhr.responseText) {
                    self.finish_loading();
                    self.render_notification('Karten geladen');
                    $('#link-list').html('');
                    var result = JSON.parse(xhr.responseText);
                    if(typeof result.items[0].cards != 'undefined') {
                        var cards = result.items[0].cards;
                        for(var i in cards) {
                            var card = cards[i];
                            self.render_card(card);
                        }
                    }
                }
            };
            xhr.send();
        } catch(e) {
            self.render_notification('Fehler', true);
            console.log(e.message);
        }
    };

    function render_favourite(favourite) {
        var $favourite = $('.favourite-template').clone();
        $favourite.removeClass('favourite-template');
        $favourite.addClass('favourite');
        $favourite.removeClass('hidden');
        $favourite.attr('data-favourite-id', favourite.id);
        $favourite.attr('data-card-id', favourite.card_id);
        $('#favourites').prepend($favourite);
        $('.card-title', $favourite).text(favourite.card_title);
        $favourite.animate({'opacity': 1}, 200);
        $favourite.off('click');
        $favourite.click(function() {
            self.search(favourite.card_id);
        });
    };

    function render_card(card) {
        var icon = card['type'] == 'fact' ? 'fa-check-circle' : 'fa-question-circle';
        var title = card['title'];
        var author = !card['author'] ? '-' : card['author'];
        var source_logo = '';
        if(card['relation_type'] == 'confluence' && card['type'] == 'idea') {
            source_logo = 'image/confluence-blue-mini.png';
        } else if(card['relation_type'] == 'jira' && card['type'] == 'idea') {
            source_logo = 'image/jira-blue-mini.png';
        }
        var external_link = card['external_link'];
        var date = new Date(card['changed'] * 1000);
        var $template = $('.card-template').clone();
        var keywords = !card['keywords'] ? '' : card['keywords'].join(',');
        var editors = !card['editors'] ? '' : card['editors'].join(', ');
        $template.removeClass('hidden');
        $template.removeClass('card-template');
        $template.attr('href', '#edit');
        $template.attr('rel', 'modal:detail');
        if(source_logo) {
            $('img.source-logo', $template).attr('src', source_logo);
        } else {
            $('img.source-logo', $template).remove();
        }
        $('p', $template).attr('data-card-id', card['id']);
        $('p', $template).attr('data-card-type', card['type']);
        $('.date', $template).text(date.getFullYear() + '/' + (date.getMonth()+1) + '/' + date.getDate());
        $('.title', $template).html(title);
        $('.fas', $template).addClass(icon);
        $('.keywords', $template).text(keywords);
        $('.author', $template).text(author);
        $('#link-list').append($template);
        $($template).off('click');
        $($template).click(function(event) {
            event.preventDefault();
            self.register_events();
            var card_id = $('p', this).attr('data-card-id');
            var is_toggled = self.is_favourite_toggled(card_id);
            var getUrl = 'http://localhost:1352/?function=Click&card_id=' + encodeURIComponent(card_id);
            var xhr = new XMLHttpRequest();
            xhr.open('GET', getUrl, true);
            xhr.send();
            $('#detail').modal();
            $('[name=card_id]', '#detail').val(card['id']);
            $('[name=title]', '#detail').val(title);
            $('[name=text]', '#detail').text(card['text']);
            $('[name=keywords]', '#detail').val(keywords);
            $('[name=external_link]', '#detail').val(external_link);
            $('[name=editors]', '#detail').val(editors);
            if(is_toggled) {
                $('#detail .far.fa-star').removeClass('far').addClass('fas');
            } else {
                $('#detail .fas.fa-star').removeClass('fas').addClass('far');
            }
            $('.edit', '#detail').off('click');
            $('.edit', '#detail').click(function(event) {
                self.register_events();
                $('#edit').modal();
                $('[name=card_id]', '#edit').val(card['id']);
                $('[name=title]', '#edit').val(card['title']);
                $('[name=text]', '#edit').text(card['text']);
                $('[name=keywords]', '#edit').val(keywords);
                $('[name=external_link]', '#edit').val(external_link);
                $('[name=editors]', '#edit').val(editors);
            });
            $('.fa-star', '#detail').off('click');
            $('.fa-star', '#detail').click(function(event) {
                self.toggle_favourite(card['id']);
            });
            return false;
        });
    };

    function store_card(func) {

        if(func == 'edit') {
            var title = $('[name=title]', '#edit').val();
            var text = $('[name=text]', '#edit').val();
            var keywords = $('[name=keywords]', '#edit').val();
            var external_link = $('[name=external_link]', '#edit').val();
            var card_id = $('[name=card_id]', '#edit').val();
            var getUrl = 'http://localhost:1352/?function=Store&title=' + encodeURIComponent(title)
                        + '&text=' + encodeURIComponent(text) + '&keywords=' + encodeURIComponent(keywords)
                        + '&external_link=' + encodeURIComponent(external_link) +
                        + '&card_id=' + encodeURIComponent(card_id);
        } else {
            var title = $('[name=title]', '#create').val();
            var text = $('[name=text]', '#create').val();
            var keywords = $('[name=keywords]', '#create').val();
            var external_link = $('[name=external_link]', '#create').val();
            var getUrl = 'http://localhost:1352/?function=Store&title=' + encodeURIComponent(title)
                        + '&text=' + encodeURIComponent(text) + '&keywords=' + encodeURIComponent(keywords)
                        + '&external_link=' + encodeURIComponent(external_link);
        }

        if(title == '' || text == '') {
            self.render_notification('Fehler: Titel und Beschreibung sind Pflichtfelder', true);
            return;
        }

        self.start_loading();
        var xhr = new XMLHttpRequest();
        xhr.open('GET', getUrl, true);
        xhr.send();
        xhr.onreadystatechange = function() {
            if(xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200 && xhr.responseText) {
                self.finish_loading();
                self.render_notification('Karte gespeichert');
                window.location.reload();
            }
        };
    };

    construct.prototype = {
        init: init,
        search: search,
        info: info,
        latest_cards: latest_cards,
        render_card: render_card,
        store_card: store_card,
        keywords: keywords,
        register_events: register_events,
        suggest_keywords: suggest_keywords,
        open_external_link: open_external_link,
        render_notification: render_notification,
        start_loading: start_loading,
        finish_loading: finish_loading,
        favourites: favourites,
        render_favourite: render_favourite,
        toggle_favourite: toggle_favourite,
        is_favourite_toggled: is_favourite_toggled
    };

    return construct;

})(window, document, jQuery);

main = new PS();