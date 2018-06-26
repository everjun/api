from aiohttp import web
from logic import check_secret_key

def json_fields_required(*fields):
    """ 
    decorator for required fields
    :param *fields: list of required fields (str type)  
    """
    def dec(f):
        async def res_func(request):
            try:
                r = await request.json()
                list_of_missing_fields = [field for field in fields if field not in r]
                if list_of_missing_fields:
                    return web.json_response({'error': True, 
                                              'error_text': 'Missing fields', 
                                              'fields': list_of_missing_fields})
                return await f(request)
            except:
                pass
            return web.json_response({'error': True, 'error_text': 'Wrong request'})
        res_func.__doc__ = f.__doc__
        return res_func
    return dec


def json_login_required(f):
    async def res_func(request):
        try:
            r = await request.json()
            if 'auth_token' in r:
                check = check_secret_key(r['auth_token'])
                if check:
                    return await f(request)
                else:
                    return web.json_response({'error': True, 'error_text': 'Your auth token is invalid'})
            else:
                return web.json_response({'error': True, 'error_text': 'Auth token required'})
        except:
            pass
        return web.json_response({'error': True, 'error_text': 'Wrong request'})
    res_func.__doc__ = f.__doc__
    return res_func