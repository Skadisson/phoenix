var main;

PS = (function(window, document, $) {

    'use strict';

    var self, weeks, mode;

    var construct = function() {
        self = this;
        self.init();
    };

    function init() {
        $('input[type=text]').focus();
        self.info();
        self.latest_cards();
    };

    function info() {
        var getUrl = 'http://localhost:1352/?function=Ping';
        var formContentType = 'application/x-www-form-urlencoded';
        try {
            var xhr = new XMLHttpRequest();
            xhr.open('GET', getUrl, true);
            xhr.setRequestHeader('Content-type', formContentType);
            xhr.onreadystatechange = function() {
                if(xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200 && xhr.responseText) {
                    $('#keywords').attr('placeholder', '');
                    var result = JSON.parse(xhr.responseText);
                    if(typeof result.items[0].idea_count != 'undefined' && typeof result.items[0].fact_count != 'undefined') {
                        $('#keywords').attr('placeholder', "Search a topic from " + result.items[0].idea_count + " ideas and " + result.items[0].fact_count + " facts");
                    }
                }
            };
            xhr.send();
        } catch(e) {
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
            xhr.onreadystatechange = function() {
                if(xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200 && xhr.responseText) {
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
            console.log(e.message);
        }
    };

    function search() {
        $('body').css('cursor', 'wait');
        var keywords = $('#keywords').val();
        var getUrl = 'http://localhost:1352/?function=Search&query=' + encodeURIComponent(keywords);
        var formContentType = 'application/x-www-form-urlencoded';
        try {
            var xhr = new XMLHttpRequest();
            xhr.open('GET', getUrl, true);
            xhr.setRequestHeader('Content-type', formContentType);
            xhr.onreadystatechange = function() {
                if(xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200 && xhr.responseText) {
                    $('body').css('cursor', 'auto');
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
            console.log(e.message);
        }
    };

    function render_card(card) {
        var icon = card['type'] == 'fact' ? 'fa-check-circle' : 'fa-question-circle';
        var title = card['title'];
        var author = !card['author'] ? '-' : card['author'];
        if(card['relation_type'] == 'confluence' && card['type'] == 'idea') {
            title = 'Confluence:<br />' + title
        } else if(card['relation_type'] == 'jira' && card['type'] == 'idea') {
            title = 'Jira:<br />' + title
        }
        var date = new Date(card['changed'] * 1000)
        var $template = $('.card-template').clone();
        var keywords = !card['keywords'] ? '' : card['keywords'].join(',')
        $template.removeClass('hidden');
        $template.removeClass('card-template');
        $template.attr('href', '#edit');
        $template.attr('rel', 'modal:detail');
        $('p', $template).attr('data-card-id', card['id']);
        $('p', $template).attr('data-card-type', card['type']);
        $('.date', $template).text(date.getFullYear() + '/' + (date.getMonth()+1) + '/' + date.getDate());
        $('.title', $template).html(title);
        $('.fas', $template).addClass(icon);
        $('.keywords', $template).text(keywords);
        $('.author', $template).text(author);
        $('#link-list').append($template);
        $($template).click(function(event) {
            event.preventDefault();
            var card_id = $('p', this).attr('data-card-id');
            var getUrl = 'http://localhost:1352/?function=Click&card_id=' + encodeURIComponent(card_id);
            var xhr = new XMLHttpRequest();
            xhr.open('GET', getUrl, true);
            xhr.send();
            $('#detail').modal();
            $('[name=card_id]', '#detail').val(card['id']);
            $('[name=title]', '#detail').val(title);
            $('[name=text]', '#detail').text(card['text']);
            $('[name=keywords]', '#detail').val(keywords);
            $('.edit', '#detail').click(function(event) {
                $('#edit').modal();
                $('[name=card_id]', '#edit').val(card['id']);
                $('[name=title]', '#edit').val(card['title']);
                $('[name=text]', '#edit').text(card['text']);
                $('[name=keywords]', '#edit').val(keywords);
            });
            return false;
        });
    };

    function store_card(func) {

        $('body').css('cursor', 'wait');
        if(func == 'edit') {
            var title = $('[name=title]', '#edit').val();
            var text = $('[name=text]', '#edit').val();
            var keywords = $('[name=keywords]', '#edit').val();
            var card_id = $('[name=card_id]', '#edit').val();
            var getUrl = 'http://localhost:1352/?function=Store&title=' + encodeURIComponent(title)
                        + '&text=' + encodeURIComponent(text) + '&keywords=' + encodeURIComponent(keywords)
                        + '&card_id=' + encodeURIComponent(card_id);
        } else {
            var title = $('[name=title]', '#create').val();
            var text = $('[name=text]', '#create').val();
            var keywords = $('[name=keywords]', '#create').val();
            var getUrl = 'http://localhost:1352/?function=Store&title=' + encodeURIComponent(title)
                        + '&text=' + encodeURIComponent(text) + '&keywords=' + encodeURIComponent(keywords);
        }

        if(title == '' || text == '') {
            $('body').css('cursor', 'wait');
            alert('Title and text are mandatory!');
            return;
        }

        var xhr = new XMLHttpRequest();
        xhr.open('GET', getUrl, true);
        xhr.send();
        xhr.onreadystatechange = function() {
            if(xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200 && xhr.responseText) {
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
        store_card: store_card
    };

    return construct;

})(window, document, jQuery);

main = new PS();