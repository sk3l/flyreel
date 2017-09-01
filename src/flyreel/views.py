from pyramid.view import view_config


@view_config(route_name='home', renderer='templates/mytemplate.jinja2')
def my_view(request):
    return {'project': 'src'}

@view_config(route_name='test', renderer='json')
def my_view_2(request):
    return {'hello': 'world'}
