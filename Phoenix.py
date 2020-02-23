from werkzeug.wrappers import Request, Response
from bin.module import Test, Ping, Update, Latest, Search, Backup, Click, Store
from bin.service import Environment
import json


@Request.application
def phoenix(request):
    function = request.args.get('function', None)
    if function == 'Test':
        test = Test.Test()
        response = test.run()
    elif function == 'Ping':
        ping = Ping.Ping()
        response = ping.run()
    elif function == 'Update':
        update = Update.Update()
        response = update.run()
    elif function == 'Latest':
        latest = Latest.Latest()
        response = latest.run()
    elif function == 'Search':
        query = request.args.get('query', None)
        search = Search.Search()
        response = search.run(query)
    elif function == 'Backup':
        backup = Backup.Backup()
        response = backup.run()
    elif function == 'Click':
        card_id = int(request.args.get('card_id', 0))
        click = Click.Click()
        response = click.run(card_id)
    elif function == 'Store':
        title = str(request.args.get('title', ''))
        text = str(request.args.get('text', ''))
        keywords = str(request.args.get('keywords', ''))
        card_id = int(request.args.get('card_id', 0))
        store = Store.Store()
        response = store.run(title, text, keywords, card_id)
    else:
        response = {'error': 'unknown function'}

    json_response = json.dumps(response)
    return Response(json_response, mimetype='application/json', headers={'Access-Control-Allow-Origin': '*'})


if __name__ == '__main__':
    from werkzeug.serving import run_simple
    env = Environment.Environment()
    port = env.get_service_port()
    host = env.get_service_host()
    run_simple(hostname=host, port=port, application=phoenix)
