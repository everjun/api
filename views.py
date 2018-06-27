import asyncio


from logic import get_secret_key, check_secret_key, add_element,\
                  get_element, get_tree, login as log
from models import User
from aiohttp import web
from aiopg.sa import create_engine
from aiohttp_swagger import setup_swagger
from settings import DATABASE_SETTINGS
from decorators import json_fields_required, json_login_required


engine = None
connection = None

async def init_engine():
    global engine
    global connection
    if not engine:
        engine = await create_engine(user=DATABASE_SETTINGS['username'],
                                     password=DATABASE_SETTINGS['password'],
                                     database=DATABASE_SETTINGS['database'],
                                     host=DATABASE_SETTINGS['host'],
                                     port=DATABASE_SETTINGS['port'])
        connection = await engine.acquire()



routes = web.RouteTableDef()

@routes.post('/api/login')
@json_fields_required('username', 'password')
async def login(request):
    """
    ---
    tags:
    - Login
    summary: Sign in into system
    produces:
    - application/json
    parameters:
    - in: body
      name: body
      required: true
      schema:
        type: object
        properties:
          username:
            type: string
            example: "everjun"
          password:
            type: string
            example: "password"
    responses:
    "200":
      description: successful operation
    """
    try:
        r = await request.json()
        user = await log(connection, r['username'], r['password'])
        if user:
            return web.json_response({'error': False, 'auth_token': get_secret_key(user).decode('utf8')})
        return web.json_response({'error': True, 'error_text': 'Wrong username or password'})
    except:
        pass
    return web.json_response({'error': True, 'error_text': 'Wrong request'})


# @app.route('/api/add', methods=['POST'])
@routes.post('/api/add')
@json_fields_required('auth_token', 'text')
@json_login_required
async def add(request):
    """
    ---
    tags:
    - Add text node
    summary: Sign in into system
    produces:
    - application/json
    parameters:
    - in: body
      name: body
      required: true
      schema:
        type: object
        properties:
          auth_token:
            type: string
            example: "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6ImV2ZXJqdW4iLCJleHAiOjE1Mjk1MTQ1MTkuMH0.V761i2tMqGC6ysdKEqDif8B99l61j7lcb4DAwzlliiY"
          text:
            type: string
            example: "Some text"
          parent_id:
            type: integer
            required: false
            example: 12
    responses:
    "200":
      description: successful operation
    """
    try:
        r = await request.json()
        parent_id = r.get('parent_id', None)
        text = r['text']
        el = await add_element(connection, text, parent_id)
        return web.json_response({'error': False, 'response':{'element':{'id': el.id, 'text': el.text, 'parent_id': str(el.parent_id)}}})
    except:
        pass
    return web.json_response({'error': True, 'error_text': 'Wrong request'})


@routes.post('/api/get_by_text')
@json_fields_required('auth_token', 'text')
@json_login_required
async def get(request):
    """
    ---
    tags:
    - Get text node by text
    summary: Sign in into system
    produces:
    - application/json
    parameters:
    - in: body
      name: body
      required: true
      schema:
        type: object
        properties:
          auth_token:
            type: string
            example: "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6ImV2ZXJqdW4iLCJleHAiOjE1Mjk1MTQ1MTkuMH0.V761i2tMqGC6ysdKEqDif8B99l61j7lcb4DAwzlliiY"
          text:
            type: string
            example: "Some text"
    responses:
    "200":
      description: successful operation
    """
    try:
        r = await request.json()
        text = r['text']
        lst = await get_element(connection, text)
        return web.json_response({'error': False, 'response':{'elements': lst}})
    except:
        pass
    return web.json_response({'error': True, 'error_text': 'Wrong request'})



@routes.post('/api/get_by_id')
@json_fields_required('auth_token', 'id')
@json_login_required
async def get_by_id(request):
    """
    ---
    tags:
    - Get text node by id
    summary: Sign in into system
    produces:
    - application/json
    parameters:
    - in: body
      name: body
      required: true
      schema:
        type: object
        properties:
          auth_token:
            type: string
            example: "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6ImV2ZXJqdW4iLCJleHAiOjE1Mjk1MTQ1MTkuMH0.V761i2tMqGC6ysdKEqDif8B99l61j7lcb4DAwzlliiY"
          id:
            type: integer
            example: 12
    responses:
    "200":
      description: successful operation
    """
    try:
        r = await request.json()
        id = r['id']
        res = await get_tree(connection, id)
        return web.json_response({'error': False, 'response':res})
    except:
        pass
    return web.json_response({'error': True, 'error_text': 'Wrong request'})




app = web.Application()
app.router.add_routes(routes)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(init_engine())
        setup_swagger(app, api_version="1.0.0")
        web.run_app(app)
    except:
        pass
    finally:
        connection.close()
        engine.close()


