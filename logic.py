import jwt
import time

from datetime import datetime
from models import User, TextTable
from settings import SECRET_KEY




async def sign_up(connection, username, password):
    u = User(username, password)
    await u.save(connection)
    return u


async def login(con, username, password):
    u = User(username, password)
    res = await u.check_user_in_database(con)
    return u if res else None 


async def add_element(connection, text, parent_id=None):
    t = TextTable(text, parent_id)
    await t.add_to_db(connection)
    return t


async def get_element(connection, text):
    res = await TextTable.get_by_text(connection, text)
    if res:
        els = []
        for r in res:
            lst = []
            parents = await r.get_parents_ids(connection)

                # while parent.parent_id:
                #     parent = await parent.get_parent(connection)
                #     lst.append(parent.id)
            els.append({'id':r.id, 'text':text, 'parents':parents})
        return els
    return []


async def get_tree(connection, id):
    r = await TextTable.get_by_id(connection, id)
    if r:
        parents = await r.get_parents_ids(connection)
        return {'id': id, 'text': r.text, 'parents': parents}
    return []


def get_secret_key(user):
    res = jwt.encode({'username': user.username, 'exp': time.mktime(datetime.now().timetuple())+86400}, SECRET_KEY)
    return res

def check_secret_key(key):
    try:
        res = jwt.decode(key, SECRET_KEY)
        if res['exp'] < time.mktime(datetime.now().timetuple()):
            return False
        return True
    except:
        return False

