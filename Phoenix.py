from werkzeug.wrappers import Request, Response
from bin.module import Ping, Latest, Search, Click, Store, Keywords, Favourite, Favourites, Analytics, ShoutOut, ShoutOuts, Notifications, AutoComplete, Name, Screenshot, Achievements
from bin.service import Environment, UserStorage
import json


@Request.application
def phoenix(request):

    user_storage = UserStorage.UserStorage()
    user_exists = user_storage.user_exists()
    if user_exists is False:
        user_storage.create_user()

    function = request.args.get('function', None)
    if function == 'Ping':
        ping = Ping.Ping()
        response = ping.run()
    elif function == 'Latest':
        latest = Latest.Latest()
        response = latest.run()
    elif function == 'Search':
        query = request.args.get('query', None)
        include_jira = request.args.get('includeJira', 'True')
        search = Search.Search()
        response = search.run(query, include_jira)
    elif function == 'AutoComplete':
        query = request.args.get('query', None)
        include_jira = request.args.get('includeJira', 'True')
        auto_complete = AutoComplete.AutoComplete()
        response = auto_complete.run(query, include_jira)
    elif function == 'Click':
        card_id = int(request.args.get('card_id', 0))
        loading_seconds = int(request.args.get('loading_seconds', 0))
        query = request.args.get('query', None)
        frontend = request.args.get('frontend', '')
        click = Click.Click()
        response = click.run(card_id, query, loading_seconds, frontend)
    elif function == 'Store':
        title = str(request.args.get('title', ''))
        text = str(request.args.get('text', ''))
        keywords = str(request.args.get('keywords', ''))
        card_id = int(request.args.get('card_id', 0))
        external_link = str(request.args.get('external_link', ''))
        store = Store.Store()
        response = store.run(title, text, keywords, external_link, card_id)
    elif function == 'Keywords':
        title = str(request.args.get('title', ''))
        text = str(request.args.get('text', ''))
        keywords = Keywords.Keywords()
        response = keywords.run(title, text)
    elif function == 'Favourite':
        card_id = int(request.args.get('card_id', 0))
        favourite = Favourite.Favourite()
        response = favourite.run(card_id)
    elif function == 'Favourites':
        favourites = Favourites.Favourites()
        response = favourites.run()
    elif function == 'Analytics':
        analytics = Analytics.Analytics()
        response = analytics.run()
    elif function == 'ShoutOut':
        card_id = int(request.args.get('card_id', 0))
        text = str(request.args.get('text', ''))
        shout_out = ShoutOut.ShoutOut()
        response = shout_out.run(card_id, text)
    elif function == 'Name':
        name = str(request.args.get('name', ''))
        name_mod = Name.Name()
        response = name_mod.run(name)
    elif function == 'ShoutOuts':
        shout_outs = ShoutOuts.ShoutOuts()
        response = shout_outs.run()
    elif function == 'Notifications':
        notifications = Notifications.Notifications()
        response = notifications.run()
    elif function == 'Screenshot':
        url = str(request.args.get('url', ''))
        screenshot = Screenshot.Screenshot()
        response = screenshot.run(url)
    elif function == 'Achievements':
        achievements = Achievements.Achievements()
        response = achievements.run()
    else:
        response = {'error': 'unknown function'}

    json_response = json.dumps(response)
    return Response(json_response, mimetype='application/json', headers={'Access-Control-Allow-Origin': '*'})


if __name__ == '__main__':
    from werkzeug.serving import run_simple
    env = Environment.Environment()
    port = env.get_service_port()
    host = env.get_service_host()
    use_ssl = env.get_use_ssl()
    if use_ssl is True:
        run_simple(hostname=host, port=port, application=phoenix, ssl_context='adhoc')
    else:
        run_simple(hostname=host, port=port, application=phoenix)
