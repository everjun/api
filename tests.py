import asyncio
import unittest

from models import TextTable, User
from aiopg.sa import create_engine
from logic import *
from settings import TEST_DATABASE_SETTINGS as settings



class TestNodes(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestNodes, self).__init__(*args, **kwargs)
        self.loop = asyncio.get_event_loop()
        self.loop.run_until_complete(self.init_connection(settings))


    def test_all(self):
        self.loop.run_until_complete(self.sign_up_user())
        self.assertIsNotNone(self.user)
        self.loop.run_until_complete(self.login())
        self.loop.run_until_complete(self.add_nodes())
        self.loop.run_until_complete(self.get_by_text())
        self.loop.run_until_complete(self.get_by_id())
        self.loop.run_until_complete(self.drop_all())
        self.loop.close()
        

    async def init_connection(self, settings):
        self.engine = await create_engine(user=settings['username'],
                                         password=settings['password'],
                                         database=settings['database'],
                                         host=settings['host'],
                                         port=settings['port'])
        self.connection = await self.engine.acquire()

    async def sign_up_user(self):
        self.user = await sign_up(self.connection, "test_username", "password")

    async def login(self):
        res = await login(self.connection, "test_username", "password")
        self.assertIsNotNone(res)
    
    async def add_nodes(self):
        self.node1 = await add_element(self.connection, "text 1")
        self.assertIsNotNone(self.node1)
        self.node2 = await add_element(self.connection, "text 2", self.node1.id)
        self.assertIsNotNone(self.node2)
        self.node3 = await add_element(self.connection, "text 3", self.node1.id)
        self.assertIsNotNone(self.node3)
        self.node4 = await add_element(self.connection, "text 4",  self.node2.id)
        self.assertIsNotNone(self.node4)

    async def get_by_text(self):
        nodes = await get_element(self.connection, "text 1")
        self.assertNotEqual(nodes, [])
        self.assertEqual(nodes[0]["id"], self.node1.id)
        self.assertEqual(nodes[0]["parents"], [])
        nodes = await get_element(self.connection, "text 4")
        self.assertNotEqual(nodes, [])
        self.assertEqual(nodes[0]["id"], self.node4.id)
        self.assertEqual(nodes[0]["parents"], [self.node1.id, self.node2.id])

    async def get_by_id(self):
        node = await get_tree(self.connection, self.node1.id)
        self.assertNotEqual(node, {})
        self.assertEqual(node["text"], self.node1.text)
        self.assertEqual(node["parents"], [])
        node = await get_tree(self.connection, self.node4.id)
        self.assertNotEqual(node, {})
        self.assertEqual(node["text"], self.node4.text)
        self.assertEqual(node["parents"], [self.node1.id, self.node2.id])

    async def drop_all(self):
        await self.connection.execute(TextTable.__table__.delete())
        await self.connection.execute(User.__table__.delete())
        await self.connection.close()


if __name__ == '__main__':
    unittest.main()