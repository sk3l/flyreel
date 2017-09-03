
from pyramid.view   import view_config
from cornice        import Service

flyreel_srv = Service(name="fs",
                path="/flyreel",
                description="flyreel server")

@view_config(route_name='home', renderer='templates/mytemplate.jinja2')
def my_view(request):
    return {'project': 'flyreel'}

#@flyreel_srv.get()
#def get_val(request):
#    return _VALUES.get(request.matchdict['val'])


@flyreel_srv.post()
def notify_repo(request):
    #key = request.matchdict['val']

    try:
        import pdb;pdb.set_trace()
        repo_data = request.json_body

        if "action" not in repo_data:
            return False
        elif repo_data['action'] != 'created':
            return False

        print("Received create event for repository '{0}'".format(repo_data['repository']['name']))

    except ValueError:
        return False
    return True

#@view_config(route_name='test', renderer='json')
#def my_view_2(request):
#    return {'hello': 'world'}
