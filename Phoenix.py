from werkzeug.wrappers import Request, Response
from bin.module import Test
from bin.service import Environment
import json


@Request.application
def phoenix(request):
    function = request.args.get('function', None)
    if function == 'Test':
        test = Test.Test()
        response = test.run()
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
