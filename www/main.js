var main;

PS = (function(window, document, $) {

    'use strict';

    var self;
    var loading = 0;
    var timer = 0;
    var interval = 0;
    var dot_interval = 0;
    var loading_seconds = 0;
    var last_search_time = 0;
    var loaded_shout_outs = [];
    var card_id_parameter = 0;
    var notify_interval = 0;
    var autocomplete_timeout = 0;
    var host_name = window.location.hostname;
    var host_protocol = 'http';
    var host_port = '8110';
    var tip_interval = 0;

    var construct = function() {
        self = this;
        card_id_parameter = self.getUrlVars()['card_id'];
        self.init();
    };

    function getUrlVars() {
        var vars = {};
        var parts = window.location.href.replace(/[?&]+([^=&]+)=([^&]*)/gi, function(m,key,value) {
            vars[key] = value;
        });
        return vars;
    };

    function init() {
        self.randomize_tips();
        self.tip_interval = setInterval(self.randomize_tips, 60000);
        self.info(function() {
            self.fill_popout_headers();
            self.shout_outs();
            if(card_id_parameter > 0) {
                self.search(card_id_parameter);
            } else {
                self.latest_cards();
            }
            self.favourites();

            $('input[type=text]').focus();
            self.register_events();
            //self.start_notifications();
        });
    };

    function randomize_tips() {
        var $tips = $('#tipOfTheDay li');
        var tip_count = $tips.length;
        var visible_tip = Math.floor((Math.random() * tip_count) + 1);
        $tips.hide();
        $('#tipOfTheDay li:nth-child(' + visible_tip + ')').show();
    };

    function register_events() {
        $('body').off('click');
        $('body').on('click', '.user-name', self.change_username);
        $('body').on('click', '.fa-bullseye', self.suggest_keywords);
        $('body').on('click', '.fa-external-link-square-alt', self.open_external_link);
        $('body #shout-out').on('click', '.fa-times-circle', function() {
            $('#shout-out input').val('');
            $('#shout-out').hide();
        });
        $('body').off('keyup');
        $('body').on('keyup', '#shout-out input[type=text]', function(event) {
            var text = $('#shout-out input').val();
            var card_id = $('#detail input[name=card_id]').val();
            if(card_id > 0 && text && event.keyCode == 13) {
                var getUrl = host_protocol + '://' + host_name + ':' + host_port + '/?function=ShoutOut&card_id=' + card_id + '&text=' + encodeURIComponent(text);
                var formContentType = 'application/x-www-form-urlencoded';
                var xhr = new XMLHttpRequest();
                xhr.open('GET', getUrl, true);
                xhr.setRequestHeader('Content-type', formContentType);
                self.start_loading();
                xhr.onreadystatechange = function() {
                    if(xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
                        self.finish_loading();
                        var result = JSON.parse(xhr.responseText);
                        if(typeof result.items[0] != 'undefined' && typeof result.items[0] != 'undefined') {
                            if(result.items[0].is_added) {
                                self.render_notification('Shout Out erfolgreich');
                                self.shout_outs();
                                var short = result.items[0]['shout_out']['short']
                                $('#shout-out input').val('');
                                $('#shout-out').hide();
                                $('.shout-outs').prepend('<p class="shout-out">' + short + ': "' + text + '"</p>');
                                $('#shout-out fieldset i').removeClass('fa-ellipsis-h');
                                $('#shout-out fieldset i').removeClass('fa-check');
                                $('#shout-out fieldset i').removeClass('fa-times');
                                $('#shout-out fieldset i').addClass('fa-check');
                            } else {
                                self.render_notification('Diese Woche bereits geteilt');
                                $('#shout-out fieldset i').removeClass('fa-ellipsis-h');
                                $('#shout-out fieldset i').removeClass('fa-check');
                                $('#shout-out fieldset i').removeClass('fa-times');
                                $('#shout-out fieldset i').addClass('fa-times');
                            }
                        } else {
                            self.render_notification('Shout Out fehlgeschlagen');
                            $('#shout-out fieldset i').removeClass('fa-ellipsis-h');
                            $('#shout-out fieldset i').removeClass('fa-check');
                            $('#shout-out fieldset i').removeClass('fa-times');
                            $('#shout-out fieldset i').addClass('fa-times');
                        }
                        self.flash_new_achievements();
                    }
                };
                xhr.send();
            }
        });
    };

    function start_loading() {
        self.start_timer();
        loading++;
        var current_progress = Math.round(100 / loading);
        if(loading == 1)
            $('#loaded').fadeIn();
        $('#loaded').val(current_progress);
        $('.loading').stop().animate({'opacity': 1}, 200);
    };

    function finish_loading() {
        if(loading > 0) {
            loading--;
        }
        if(loading == 0) {
            $('#loaded').val(100);
            $('#loaded').fadeOut();
        } else {
            var current_progress = Math.round(100 / loading);
            $('#loaded').val(current_progress);
        }
        if(loading == 0) {
            self.stop_timer();
            $('.loading').stop().animate({'opacity': 0}, 200);
        }
    };

    function start_timer() {
      if(!interval) {
          loading_seconds = 0;
          $('.timer').text(loading_seconds);
          interval = setInterval(function() {
            loading_seconds += 1;
            $('.timer').text(loading_seconds);
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

    function change_username() {
        var user_name = prompt("Vor- und Nachname", '');
        if(user_name == null) {
            return;
        }
        while(user_name.split(" ").length == 1) {
            user_name = prompt("Vor- und Nachname (getrennt mit Leerzeichen)", user_name);
        }
        var getUrl = host_protocol + '://' + host_name + ':' + host_port + '/?function=Name&name=' + encodeURIComponent(user_name);
        var formContentType = 'application/x-www-form-urlencoded';
        try {
            var xhr = new XMLHttpRequest();
            xhr.open('GET', getUrl, true);
            xhr.setRequestHeader('Content-type', formContentType);
            self.start_loading();
            xhr.onreadystatechange = function() {
                if(xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200 && xhr.responseText) {
                    self.finish_loading();
                    var result = JSON.parse(xhr.responseText);
                    if(typeof result.message != 'undefined') {
                        self.render_notification(result.message);
                    }
                    if(typeof result.success != 'undefined' && result.success == true) {
                        self.info();
                    }
                    self.flash_new_achievements();
                }
            };
            xhr.send();
        } catch(e) {
            self.finish_loading();
            self.render_notification('Fehler', true);
            console.log(e.message);
        }
    };

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
        var getUrl = host_protocol + '://' + host_name + ':' + host_port + '/?function=Analytics';
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
                        $('.jira-count').text(result.items[0].jira_count);
                        $('.confluence-count').text(result.items[0].confluence_count);
                        $('.git-count').text(result.items[0].git_count);
                        $('.total-count').text(result.items[0].fact_count + result.items[0].idea_count);
                        $('.click-count').text(result.items[0].click_count);
                        $('.query-count').text(result.items[0].query_count);
                        $('.desktop-count').text(result.items[0].desktop_count);
                        $('.mobile-count').text(result.items[0].mobile_count);
                        $('.favourite-count').text(result.items[0].favourite_count);
                        $('.shout-out-count').text(result.items[0].shout_out_count);
                        $('.new-facts-this-week').text(result.items[0].new_facts_this_week);
                        $('.new-facts-this-month').text(result.items[0].new_facts_this_month);
                        $('.average-loading-time').text(result.items[0].average_loading_time);
                        if(result.items[0].is_git_active) {
                            $('.is-git-active').text('Ja');
                        } else {
                            $('.is-git-active').text('Nein');
                        }
                        $('.log-entries p').remove();
                        if(result.items[0].log_entries.length > 0) {
                            for(var index in result.items[0].log_entries) {
                                $('.log-entries').prepend('<p class="log">' + result.items[0].log_entries[index] + '</p>')
                            }
                        } else {
                            $('.log-entries').prepend('<p class="log">Keine Einträge vorhanden</p>')
                        }
                        $('#analytics').show();
                        self.flash_new_achievements();
                    }
                }
            };
            xhr.send();
        } catch(e) {
            self.finish_loading();
            self.render_notification('Fehler', true);
            console.log(e.message);
        }
    };

    function toggle_achievements() {
        if($('#achievements').is(':not(:hidden)')) {
            $('#achievements').hide();
            return;
        }
        var getUrl = host_protocol + '://' + host_name + ':' + host_port + '/?function=Achievements';
        var formContentType = 'application/x-www-form-urlencoded';
        try {
            var xhr = new XMLHttpRequest();
            xhr.open('GET', getUrl, true);
            xhr.setRequestHeader('Content-type', formContentType);
            self.start_loading();
            xhr.onreadystatechange = function() {
                if(xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200 && xhr.responseText) {
                    self.finish_loading();
                    self.render_notification('Achievements');
                    var result = JSON.parse(xhr.responseText);
                    if(typeof result.items[0] != 'undefined' && typeof result.items[0] != 'undefined') {
                        $('#achievements p').remove();
                        var achievement_count = result.items[0]['achievements'].length;
                        for(var i = 0; i < achievement_count; i++) {
                            var achievement = result.items[0]['achievements'][i];
                            $('#achievements').append('<p class="' + achievement['type'] + '"><span class="fas fa-medal"> </span><span class="label">' + achievement['title'] + '</span> ● ' + achievement['description'] + '</p>');
                        }
                        $('#achievements').show();
                        self.flash_new_achievements();
                    }
                }
            };
            xhr.send();
        } catch(e) {
            self.finish_loading();
            self.render_notification('Fehler', true);
            console.log(e.message);
        }
    };

    function flash_new_achievements() {
        var getUrl = host_protocol + '://' + host_name + ':' + host_port + '/?function=Achievements';
        var formContentType = 'application/x-www-form-urlencoded';
        try {
            var xhr = new XMLHttpRequest();
            xhr.open('GET', getUrl, true);
            xhr.setRequestHeader('Content-type', formContentType);
            self.start_loading();
            xhr.onreadystatechange = function() {
                if(xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200 && xhr.responseText) {
                    self.finish_loading();
                    var result = JSON.parse(xhr.responseText);
                    if(typeof result.items[0] != 'undefined' && typeof result.items[0] != 'undefined') {
                        var achievement_count = result.items[0]['new_achievements'].length;
                        for(var i = 0; i < achievement_count; i++) {
                            var achievement = result.items[0]['new_achievements'][i];
                            var $newAchievement = $('<p class="new-achievement"><span class="info">Neues Achievement<br /></span><span class="fas fa-star spin"> </span><span class="label">' + achievement['title'] + '</span></p>');
                            $('body').append($newAchievement);
                            $newAchievement.hide();
                            $newAchievement.fadeIn();
                            setTimeout(function() {
                                $newAchievement.fadeOut();
                            }, 6000);
                        }
                    }
                }
            };
            xhr.send();
        } catch(e) {
            self.finish_loading();
            self.render_notification('Fehler', true);
            console.log(e.message);
        }
    };

    function shout_outs() {
        var getUrl = host_protocol + '://' + host_name + ':' + host_port + '/?function=ShoutOuts';
        var formContentType = 'application/x-www-form-urlencoded';
        try {
            var xhr = new XMLHttpRequest();
            xhr.open('GET', getUrl, true);
            xhr.setRequestHeader('Content-type', formContentType);
            self.start_loading();
            xhr.onreadystatechange = function() {
                if(xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200 && xhr.responseText) {
                    self.finish_loading();
                    self.render_notification('Shout Outs geladen');
                    var result = JSON.parse(xhr.responseText);
                    if(typeof result.items[0].shout_outs != 'undefined') {
                        loaded_shout_outs = result.items[0].shout_outs;
                    }
                    self.flash_new_achievements();
                }
            };
            xhr.send();
        } catch(e) {
            self.finish_loading();
            self.render_notification('Fehler', true);
            console.log(e.message);
        }
    };

    function render_shout_outs() {
        for(var i in loaded_shout_outs) {
            var loaded_shout_out = loaded_shout_outs[i];
            $('p[data-card-id=' + loaded_shout_out.card_id + ']').addClass('flash-card');
            $('p[data-card-id=' + loaded_shout_out.card_id + '] .type i').removeClass('fa-check-circle');
            $('p[data-card-id=' + loaded_shout_out.card_id + '] .type i').removeClass('fa-question-circle');
            $('p[data-card-id=' + loaded_shout_out.card_id + '] .type i').addClass('fa-bullhorn');
        }
    };

    function autoComplete(event) {
        if(event.keyCode == 13)
            return;

        var query = $('#keywords').val();
        if(query.length >= 2) {
            if(autocomplete_timeout)
                clearTimeout(autocomplete_timeout);
            autocomplete_timeout = setTimeout(function() {

                var getUrl = host_protocol + '://' + host_name + ':' + host_port + '/?function=AutoComplete';
                var formContentType = 'application/x-www-form-urlencoded';
                var query = $('#keywords').val();
                getUrl += '&query=' + query;

                try {
                    var xhr = new XMLHttpRequest();
                    xhr.open('GET', getUrl, true);
                    self.start_loading();
                    xhr.setRequestHeader('Content-type', formContentType);
                    xhr.onreadystatechange = function() {
                        if(xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200 && xhr.responseText) {
                            self.finish_loading();
                            self.render_notification('Auto-Complete');
                            $('#auto-complete option').remove();
                            var result = JSON.parse(xhr.responseText);
                            if(typeof result.items[0].suggestions != 'undefined') {
                                for(var i in result.items[0].suggestions) {
                                    var suggestion = result.items[0].suggestions[i];
                                    $('#auto-complete').append('<option value="' + suggestion + '"/>');
                                }
                            }
                            if(autocomplete_timeout)
                                clearTimeout(autocomplete_timeout);
                            self.flash_new_achievements();
                        }
                    };
                    xhr.send();
                } catch(e) {
                    self.finish_loading();
                    self.render_notification('Fehler', true);
                    console.log(e.message);
                }

            }, 700);
        }
    };

    function info(callback) {
        var getUrl = host_protocol + '://' + host_name + ':' + host_port + '/?function=Ping';
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
                    if(typeof result.items[0].user_name != 'undefined' && typeof result.items[0].user_short != 'undefined') {
                        $('p', '.user-name').remove();
                        $('.user-name').append('<p>' + result.items[0].user_name + ' (' + result.items[0].user_short + ')</p>');
                    }
                    if(typeof result.items[0].idea_count != 'undefined' && typeof result.items[0].fact_count != 'undefined') {
                        $('#keywords').attr('placeholder', "Suche Dein Thema in " + result.items[0].idea_count + " Ideen und " + result.items[0].fact_count + " Fakten");
                        var total_count = result.items[0].idea_count + result.items[0].fact_count;
                        if(total_count > 10000)
                            total_count = 10000
                        var i = 0;
                        while(i<total_count) {
                            $('.dot-space').append('<div class="dot" />');
                            i += 1;
                        }
                        if(callback && total_count > 0) {
                            callback();
                        } else if(callback && total_count <= 0) {
                            $('#keywords').val('Die Datenbank ist leer, meldet euch bei Sebastian');
                            $('#keywords').attr('readonly', true);
                            $('#link-list').remove();
                            $('.link-list').remove();
                            $('.fa-notes-medical').remove();
                        }
                        self.flash_new_achievements();
                    }
                }
            };
            xhr.send();
        } catch(e) {
            self.finish_loading();
            self.render_notification('Fehler', true);
            console.log(e.message);
        }
    };

    function favourites() {
        var getUrl = host_protocol + '://' + host_name + ':' + host_port + '/?function=Favourites';
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
                    var result = JSON.parse(xhr.responseText);
                    if(result.items.length > 0 && typeof result.items[0].favourites != 'undefined') {
                        if(result.items[0].favourites.length > 0) {
                            $('.bottom-left').hide();
                        }
                        $('#favourites').html('');
                        var favourites = result.items[0].favourites;
                        for(var i in favourites) {
                            var favourite = favourites[i];
                            self.render_favourite(favourite);
                        }
                    }
                    self.flash_new_achievements();
                }
            };
            xhr.send();
        } catch(e) {
            self.finish_loading();
            self.render_notification('Fehler', true);
            console.log(e.message);
        }
    };

    function is_favourite_toggled(card_id) {
        return $('.favourite[data-card-id=' + card_id + ']').length > 0;
    };

    function shout_out(card_id) {
        $('#shout-out fieldset i').removeClass('fa-ellipsis-h');
        $('#shout-out fieldset i').removeClass('fa-check');
        $('#shout-out fieldset i').removeClass('fa-times');
        $('#shout-out fieldset i').addClass('fa-ellipsis-h');
        $('#shout-out input').val('');
        $('#shout-out').show();
    };

    function toggle_favourite(card_id) {
        var getUrl = host_protocol + '://' + host_name + ':' + host_port + '/?function=Favourite&card_id=' + card_id;
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
                    self.flash_new_achievements();
                }
            };
            xhr.send();
        } catch(e) {
            self.finish_loading();
            self.render_notification('Fehler', true);
            console.log(e.message);
        }

    };

    function latest_cards() {
        var getUrl = host_protocol + '://' + host_name + ':' + host_port + '/?function=Latest';
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
                        self.render_shout_outs();
                    }
                    self.render_screenshots();
                    self.flash_new_achievements();
                }
            };
            xhr.send();
        } catch(e) {
            self.finish_loading();
            self.render_notification('Fehler', true);
            console.log(e.message);
        }
    };

    function keywords(title, text, $keyword_field) {
        var getUrl = host_protocol + '://' + host_name + ':' + host_port + '/?function=Keywords&title=' + encodeURIComponent(title) + '&text=' + encodeURIComponent(text);
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
                    self.flash_new_achievements();
                }
            };
            xhr.send();
        } catch(e) {
            self.finish_loading();
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
        $('#auto-complete option').remove();
        self.start_dot_animation();
        if(card_id != null) {
            var getUrl = host_protocol + '://' + host_name + ':' + host_port + '/?function=Search&query=' + encodeURIComponent(card_id);
        } else {
            var keywords = $('#keywords').val();
            var getUrl = host_protocol + '://' + host_name + ':' + host_port + '/?function=Search&query=' + encodeURIComponent(keywords);
        }
        var formContentType = 'application/x-www-form-urlencoded';
        try {
            var xhr = new XMLHttpRequest();
            xhr.open('GET', getUrl, true);
            xhr.setRequestHeader('Content-type', formContentType);
            self.start_loading();
            xhr.onreadystatechange = function() {
                if(xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200 && xhr.responseText) {
                    last_search_time = loading_seconds
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
                        self.render_shout_outs();
                        if(result.items[0].count == 0) {
                            $('.nothing-found').show();
                        } else {
                            $('.nothing-found').hide();
                        }
                    }
                    self.render_screenshots();
                    self.flash_new_achievements();
                }
            };
            xhr.send();
        } catch(e) {
            self.finish_loading();
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
        if(card['relation_type'] == 'confluence') {
            source_logo = 'image/confluence-logo.png';
        } else if(card['relation_type'] == 'jira') {
            source_logo = 'image/jira4.png';
        } else if(card['relation_type'] == 'git') {
            source_logo = 'image/GitLab_Logo.png';
        } else {
            source_logo = 'image/phoenix_logo.png';
        }
        var external_link = card['external_link'];
        var date = new Date(card['changed'] * 1000);
        var $template = $('.card-template').clone();
        var keywords = !card['keywords'] ? '' : card['keywords'].join(', ');
        var editors = !card['editors'] ? '' : card['editors'].join(', ');
        $template.removeClass('hidden');
        $template.removeClass('card-template');
        $template.attr('href', '');
        $template.attr('rel', 'modal:detail');
        if(source_logo) {
            $('img.source-logo', $template).attr('src', source_logo);
        } else {
            $('img.source-logo', $template).remove();
        }
        $('.source-tooltip', $template).text((card['relation_type'] ? card['relation_type'] : 'phoenix'));
        $('p', $template).attr('data-card-id', card['id']);
        $('p', $template).attr('data-card-type', card['type']);
        $('p', $template).attr('data-card-link', external_link);
        $('.date', $template).text(date.getFullYear() + '/' + (date.getMonth()+1) + '/' + date.getDate());
        $('.title', $template).html(title);
        $('.type .fas', $template).addClass(icon);
        if(card['probability']) {
            $('.probability').html('<i class="fas fa-bullseye"></i> ' + (Math.round(card['probability'] * 10000)) + ' %');
        } else {
            $('.probability').html('');
        }
        $('.keywords', $template).text(keywords);
        $('.author', $template).text(author);
        $('#link-list').append($template);
        $($template).off('click');
        $($template).on('click', function(event) {
            event.preventDefault();
            var card_id = $('p', $template).attr('data-card-id');
            var query = $('#keywords').val();
            var getUrl = host_protocol + '://' + host_name + ':' + host_port + '/?function=Click&card_id=' + encodeURIComponent(card_id) + '&query=' + encodeURIComponent(query) + '&loading_seconds=' + encodeURIComponent(last_search_time) + '&frontend=desktop';
            var xhr = new XMLHttpRequest();
            xhr.open('GET', getUrl, true);
            xhr.send();
            var external_link = $('p', $template).attr('data-card-link');
            if(external_link != '') {
                window.open(external_link);
            }
            self.flash_new_achievements();
        });
        $('.edit', $template).on('click', function(event) {
            event.preventDefault();
            self.register_events();
            var card_id = $('p', $template).attr('data-card-id');
            var is_toggled = self.is_favourite_toggled(card_id);
            var query = $('#keywords').val();
            var getUrl = host_protocol + '://' + host_name + ':' + host_port + '/?function=Click&card_id=' + encodeURIComponent(card_id) + '&query=' + encodeURIComponent(query) + '&loading_seconds=' + encodeURIComponent(loading_seconds) + '&frontend=desktop';
            var xhr = new XMLHttpRequest();
            xhr.open('GET', getUrl, true);
            xhr.send();
            $('#detail').modal();
            $('#detail .screenshot').css('background-image', $('p[data-card-id=' + card_id + '] .screenshot').css('background-image'));
            $('.jquery-modal.blocker').css('background-image', $('p[data-card-id=' + card_id + '] .screenshot').css('background-image'));
            $('[name=card_id]', '#detail').val(card['id']);
            $('[name=title]', '#detail').val(card['title']);
            $('[name=text]', '#detail').val(card['text']);
            $('[name=keywords]', '#detail').val(keywords);
            $('[name=external_link]', '#detail').val(external_link);
            $('[name=editors]', '#detail').val(editors);
            $('.shout-outs p', '#detail').remove();
            for(var x in loaded_shout_outs) {
                var loaded_shout_out = loaded_shout_outs[x];
                if(loaded_shout_out.card_id == card['id']) {
                    $('.shout-outs').prepend('<p class="shout-out">' + loaded_shout_out['name'] + ': "' + loaded_shout_out['text'] + '"</p>');
                }
            }
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
                $('[name=text]', '#edit').val(card['text']);
                $('[name=keywords]', '#edit').val(keywords);
                $('[name=external_link]', '#edit').val(external_link);
                $('[name=editors]', '#edit').val(editors);
            });
            $('.fa-star', '#detail').off('click');
            $('.fa-star', '#detail').click(function(event) {
                self.toggle_favourite(card['id']);
            });
            $('.fa-bullhorn', '#detail').off('click');
            $('.fa-bullhorn', '#detail').click(function(event) {
                self.shout_out(card['id']);
            });
            return false;
        });
    };

    function render_screenshots() {
        $('p[data-card-id]').each(function() {
            var card_id = $(this).data('card-id');
            if(parseInt(card_id) > 0) {
                self.render_screenshot(card_id);
            }
        });
    };

    function render_screenshot(card_id) {
        var $screenshotCard = $('p[data-card-id=' + card_id + ']');
        var url = "" + $screenshotCard.data('card-link');
        if(url == '')
            return;

        var getUrl = host_protocol + '://' + host_name + ':' + host_port + '/?function=Screenshot&url=' + encodeURI(url);
        var formContentType = 'application/x-www-form-urlencoded';
        try {
            var xhr = new XMLHttpRequest();
            xhr.open('GET', getUrl, true);
            xhr.setRequestHeader('Content-type', formContentType);
            self.start_loading();
            xhr.onreadystatechange = function() {
                if(xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200 && xhr.responseText) {
                    self.finish_loading();
                    var result = JSON.parse(xhr.responseText);
                    if(result.items.length > 0) {
                        var screenshot = result.items[0];
                        self.render_notification('Screenshot geladen');
                        $('.screenshot', $screenshotCard).css({'background-image': 'url(screenshots/' + screenshot + ')'});
                    }
                }
            };
            xhr.send();
        } catch(e) {
            self.finish_loading();
            self.render_notification('Fehler', true);
            console.log(e.message);
        }
    };

    function store_card(func) {

        var card_id = 0;
        if(func == 'edit') {
            var title = $('[name=title]', '#edit').val();
            var text = $('[name=text]', '#edit').val();
            var keywords = $('[name=keywords]', '#edit').val();
            var external_link = $('[name=external_link]', '#edit').val();
            card_id = $('[name=card_id]', '#edit').val();
            var getUrl = host_protocol + '://' + host_name + ':' + host_port + '/?function=Store&title=' + encodeURIComponent(title)
                        + '&keywords=' + encodeURIComponent(keywords)
                        + '&card_id=' + encodeURIComponent(card_id)
                        + '&text=' + encodeURIComponent(text)
                        + '&external_link=' + encodeURIComponent(external_link);
        } else {
            var title = $('[name=title]', '#create').val();
            var text = $('[name=text]', '#create').val();
            var keywords = $('[name=keywords]', '#create').val();
            var external_link = $('[name=external_link]', '#create').val();
            var getUrl = host_protocol + '://' + host_name + ':' + host_port + '/?function=Store&title=' + encodeURIComponent(title)
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
                if(card_id > 0) {
                    var $changed_card = $('[data-card-id=' + card_id + ']');
                    $('.date', $changed_card).text('soeben geändert');
                    $('.title', $changed_card).text(title);
                    $('.author', $changed_card).text('');
                    $('.keywords', $changed_card).text(keywords);
                }
                self.finish_loading();
                self.render_notification('Karte gespeichert');
                if(card_id > 0) {
                    self.search(card_id);
                    $('#keywords').val('');
                } else {
                    self.search();
                }
                self.favourites();
                $('[name=title]', '#create').val('');
                $('[name=text]', '#create').val('');
                $('[name=keywords]', '#create').val('');
                $('[name=external_link]', '#create').val('');
            }
        };
    };

    function fill_popout_headers() {
        var $analyticsHeader = $('#analytics .header');
        var $achievementsHeader = $('#achievements .header');
        for(var i = 0; i<996; i++) {
            $analyticsHeader.append('<div class="analytics-dot" />');
            $achievementsHeader.append('<div class="achievements-dot" />');
        }
    };

    function start_notifications() {
        self.request_notifications();
        if(self.notify_interval == 0) {
            self.notify_interval = setInterval(self.request_notifications, 60000);
        }
    };

    function request_notifications() {
        navigator.serviceWorker.register('service-worker.js', {scope: 'http://' + host_name + ':8080/'}).then(registration => {

            var getUrl = host_protocol + '://' + host_name + ':' + host_port + '/?function=Notifications';
            var formContentType = 'application/x-www-form-urlencoded';
            try {
                var xhr = new XMLHttpRequest();
                xhr.open('GET', getUrl, true);
                xhr.setRequestHeader('Content-type', formContentType);
                self.start_loading();
                xhr.onreadystatechange = function() {
                    if(xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200 && xhr.responseText) {
                        self.finish_loading();
                        self.render_notification('Benachrichtigungen aktualisiert');
                        var result = JSON.parse(xhr.responseText);
                        if(typeof result.items[0].notifications != 'undefined') {
                            for(var i in result.items[0].notifications) {
                                var notification = result.items[0].notifications[i];
                                var title = 'Phoenix: ';
                                if(notification['is_shout_out']) {
                                    title += 'Neuer ShoutOut';
                                } else {
                                    title += 'Neuer Fakt';
                                }
                                var options = {
                                    icon: 'favicon-32x32.png',
                                    silent: true,
                                    body: notification['title']
                                };
                                registration.showNotification(title, options);
                            }
                            self.flash_new_achievements();
                        }
                    }
                };
                xhr.send();
            } catch(e) {
                self.finish_loading();
                self.render_notification('Fehler', true);
                console.log(e.message);
            }

        }).catch((error) => {
            console.log('Registration failed with ' + error);
        });
    };

    construct.prototype = {
        init: init,
        search: search,
        info: info,
        latest_cards: latest_cards,
        render_card: render_card,
        render_screenshots: render_screenshots,
        render_screenshot: render_screenshot,
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
        shout_out: shout_out,
        is_favourite_toggled: is_favourite_toggled,
        start_dot_animation: start_dot_animation,
        stop_dot_animation: stop_dot_animation,
        randomize: randomize,
        toggle_analytics: toggle_analytics,
        toggle_achievements: toggle_achievements,
        fill_popout_headers: fill_popout_headers,
        shout_outs: shout_outs,
        render_shout_outs: render_shout_outs,
        getUrlVars: getUrlVars,
        start_notifications: start_notifications,
        request_notifications: request_notifications,
        autoComplete: autoComplete,
        change_username: change_username,
        randomize_tips: randomize_tips,
        flash_new_achievements: flash_new_achievements
    };

    return construct;

})(window, document, jQuery);

$(document).ready(function() {
    main = new PS();
});