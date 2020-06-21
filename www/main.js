var main;

PS = (function(window, document, $) {

    'use strict';

    var self;
    var loading = 0;
    var timer = 0;
    var interval = 0;
    var dot_interval = 0;

    var construct = function() {
        self = this;
        self.init();
    };

    function init() {
        self.fill_analytics();
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
        self.start_timer();
        loading++;
        $('.loading').stop().animate({'opacity': 1}, 200);
    };

    function finish_loading() {
        loading--;
        if(loading == 0) {
            self.stop_timer();
            $('.loading').stop().animate({'opacity': 0}, 200);
        }
    };

    function start_timer() {
      if(!interval) {
          timer = 0;
          $('.timer').text(timer);
          interval = setInterval(function() {
            timer += 1;
            $('.timer').text(timer);
          }, 1000);
      }
    };

    function stop_timer() {
      if(interval) {
        clearInterval(interval);
        interval = 0;
      }
    };

    function randomize(value) {
        return Math.random()*value;
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

    function toggle_analytics() {
        if($('#analytics').is(':not(:hidden)')) {
            $('#analytics').hide();
            return;
        }
        var getUrl = 'http://localhost:1352/?function=Analytics';
        var formContentType = 'application/x-www-form-urlencoded';
        try {
            var xhr = new XMLHttpRequest();
            xhr.open('GET', getUrl, true);
            xhr.setRequestHeader('Content-type', formContentType);
            self.start_loading();
            xhr.onreadystatechange = function() {
                if(xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200 && xhr.responseText) {
                    self.finish_loading();
                    self.render_notification('Analytics geladen');
                    var result = JSON.parse(xhr.responseText);
                    if(typeof result.items[0] != 'undefined' && typeof result.items[0] != 'undefined') {
                        $('.fact-count').text(result.items[0].fact_count);
                        $('.idea-count').text(result.items[0].idea_count);
                        $('.total-count').text(result.items[0].fact_count + result.items[0].idea_count);
                        $('.click-count').text(result.items[0].click_count);
                        $('.query-count').text(result.items[0].query_count);
                        $('.favourite-count').text(result.items[0].favourite_count);
                        $('.new-facts-this-week').text(result.items[0].new_facts_this_week);
                        $('.new-facts-this-month').text(result.items[0].new_facts_this_month);
                        $('.log-entries p').remove();
                        for(var index in result.items[0].log_entries) {
                            $('.log-entries').prepend('<p class="log">' + result.items[0].log_entries[index] + '</p>')
                        }
                        $('#analytics').show();
                    }
                }
            };
            xhr.send();
        } catch(e) {
            self.render_notification('Fehler', true);
            console.log(e.message);
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
                        var total_count = result.items[0].idea_count + result.items[0].fact_count;
                        var i = 0;
                        while(i<total_count) {
                            $('.dot-space').append('<div class="dot" />');
                            i += 1;
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
            self.start_dot_animation();
            xhr.onreadystatechange = function() {
                if(xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200 && xhr.responseText) {
                    self.finish_loading();
                    $('#link-list').html('');
                    var result = JSON.parse(xhr.responseText);
                    if(typeof result.items[0].cards != 'undefined') {
                        var cards = result.items[0].cards;
                        self.render_notification(result.items[0].count + ' Karte(n) geladen');
                        for(var i in cards) {
                            var card = cards[i];
                            self.render_card(card);
                        }
                        self.stop_dot_animation(result.items[0].count);
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

    function start_dot_animation() {
        if(dot_interval){
            clearInterval(dot_interval);
            dot_interval = 0;
        }
        $('.dot.active').removeClass('active');
        $('.dot').addClass('active');
        dot_interval = setInterval(function() {
            var $active_dots = $('.dot.active');
            var deactivate_dots = ($active_dots.length / 2) - 8;
            var occured = [];
            if(deactivate_dots > 0) {
                for(var i = 0; i < deactivate_dots; i++) {
                    var random = Math.floor(self.randomize($active_dots.length));
                    while($.inArray(random, occured) != -1) {
                        var random = Math.floor(self.randomize($active_dots.length));
                    }
                    occured.push(random);
                    $($active_dots[random]).removeClass('active');
                }
            } else {
                clearInterval(dot_interval);
            }
        }, 1000);
    };

    function stop_dot_animation(count_cards) {
        if(dot_interval){
            clearInterval(dot_interval);
            dot_interval = 0;
        }
        var $active_dots = $('.dot.active');
        var $inactive_dots = $('.dot:not(.active)');
        var occured = [];
        if($active_dots.length > count_cards) {
            var diff = $active_dots.length - count_cards;
            var total_count = $active_dots.length;
            for(var i = 0; i < diff; i++) {
                var random = Math.floor(self.randomize(total_count));
                while($.inArray(random, occured) != -1) {
                    var random = Math.floor(self.randomize(total_count));
                }
                occured.push(random);
                $($active_dots[random]).removeClass('active');
            }
        } else if($active_dots.length < count_cards) {
            var diff = count_cards - $active_dots.length;
            var total_count = $inactive_dots.length;
            for(var i = 0; i < diff; i++) {
                var random = Math.floor(self.randomize(total_count));
                while($.inArray(random, occured) != -1) {
                    var random = Math.floor(self.randomize(total_count));
                }
                occured.push(random);
                $($inactive_dots[random]).addClass('active');
            }
        }
    };

    function search(card_id=null) {
        self.start_dot_animation();
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
                    $('#link-list').html('');
                    var result = JSON.parse(xhr.responseText);
                    if(typeof result.items[0].cards != 'undefined') {
                        var cards = result.items[0].cards;
                        self.render_notification(result.items[0].count + ' Karten geladen');
                        for(var i in cards) {
                            var card = cards[i];
                            self.render_card(card);
                        }
                        self.stop_dot_animation(result.items[0].count);
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
            source_logo = 'image/confluence-logo.png';
        } else if(card['relation_type'] == 'jira' && card['type'] == 'idea') {
            source_logo = 'image/jira4.png';
        } else if(card['relation_type'] == 'git' && card['type'] == 'idea') {
            source_logo = 'image/GitLab_Logo.png';
        } else {
            source_logo = 'image/phoenix_logo.png';
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
        $('.source-tooltip', $template).text((card['relation_type'] ? card['relation_type'] : 'phoenix'));
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
            var query = $('#keywords').val();
            var getUrl = 'http://localhost:1352/?function=Click&card_id=' + encodeURIComponent(card_id) + '&query=' + encodeURIComponent(query);
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
                        + '&keywords=' + encodeURIComponent(keywords)
                        + '&card_id=' + encodeURIComponent(card_id)
                        + '&text=' + encodeURIComponent(text)
                        + '&external_link=' + encodeURIComponent(external_link);
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
                self.search();
            }
        };
    };

    function fill_analytics() {
        var $header = $('#analytics .header');
        for(var i = 0; i<3000; i++) {
            $header.append('<div class="analytics-dot" />');
        }
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
        start_timer: start_timer,
        stop_timer: stop_timer,
        favourites: favourites,
        render_favourite: render_favourite,
        toggle_favourite: toggle_favourite,
        is_favourite_toggled: is_favourite_toggled,
        start_dot_animation: start_dot_animation,
        stop_dot_animation: stop_dot_animation,
        randomize: randomize,
        toggle_analytics: toggle_analytics,
        fill_analytics: fill_analytics
    };

    return construct;

})(window, document, jQuery);

main = new PS();