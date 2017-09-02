from pyramid.view import view_config

from cornice import Service

_VALUES = {}

flyreel_srv = Service(name="fs",
                path="/flyreel/{val}",
                description="flyreel server")

@view_config(route_name='home', renderer='templates/mytemplate.jinja2')
def my_view(request):
    return {'project': 'flyreel'}

@flyreel_srv.get()
def get_val(request):
    return _VALUES.get(request.matchdict['val'])


@flyreel_srv.post()
def set_val(request):
    key = request.matchdict['val']

    try:
        _VALUES[key] = request.json_body
    except ValueError:
        return False
    return True

#@view_config(route_name='test', renderer='json')
#def my_view_2(request):
#    return {'hello': 'world'}
