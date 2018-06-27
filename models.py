import aiopg


from sqlalchemy import Column, Integer, String, ForeignKey, func
from sqlalchemy.sql.expression import exists, literal, and_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship
from hashlib import md5
from aiopg.sa import create_engine



Base = declarative_base()

class TextTable(Base):
    __tablename__ = 'texttable'
    id = Column(Integer, primary_key=True)
    text = Column(String)
    path = Column(String)

    def __init__(self, text, parent_id=None, path=None):
        self.text = text
        self.parent_id = parent_id
        self.path = path


    def __str__(self):
        return "<TextTable %i, %s, %s>" % (self.id, self.text, self.parent_id)


    async def add_to_db(self, connection):
        res = await connection.execute(TextTable.__table__.insert().values(text=self.text, 
                                                                           path=await self.get_path(connection)))
        row = await res.fetchone()
        self.id = row["id"]

    async def get_parent(self, connection):
        if self.parent_id:
            return await TextTable.get_by_id(connection, self.parent_id)
        return None

    async def get_path(self, connection):
        path = await connection.execute(TextTable.__table__.select()\
                                                             .where(TextTable.id == self.parent_id)\
                                                             .column(TextTable.path))
        if path.rowcount == 1:
            path = (await path.fetchone())["path"]
            children_count = await connection.execute(TextTable.__table__.select()\
                                                                          .where(TextTable.path.startswith("%s." % path))\
                                                                          .where(TextTable.path.notlike("%s.%%.%%" % path)))
            self.path = "%s.%i" % (path, children_count.rowcount + 1)
            return self.path
        elif self.parent_id is not None:
            raise Exception('Wrong parent id')
        self.path = None
        return None

    async def get_parents_ids(self, connection):
        if not self.path:
            self.get_path(connection)
        rows = await connection.execute(TextTable.__table__.select()\
                                                           .where(and_(literal(self.path).startswith(TextTable.path),
                                                                       TextTable.id != self.id)))
        lst = []
        async for row in rows:
            lst.append(row["id"])
        return lst


    @classmethod
    async def get_by_text(cls, connection, text):
        res = await connection.execute(TextTable.__table__.select().where(TextTable.__table__.c.text == text))
        if res.rowcount > 0:
            lst = []
            async for row in res:
                t = TextTable(text, path=row["path"])
                t.id = row["id"]
                lst.append(t)
            return lst
        return []


    @classmethod
    async def get_by_id(cls, connection, id):
        res = await connection.execute(TextTable.__table__.select().where(TextTable.__table__.c.id == id))
        if res.rowcount == 1:
            lst = []
            row = await res.fetchone()
            t = TextTable(row["text"], path=row["path"])
            t.id = id
            return t
        return None



class User(Base):
    __tablename__ = 'users'
    username = Column(String, primary_key=True)
    password = Column(String)

    def __init__(self, username, password):
        self.username = username
        self.password = password


    def __setattr__(self, name, value):
        if name == 'password':
            self.__dict__['password'] = User.hash_password(value)
        else:
            super(User, self).__setattr__(name, value)


    def __str__(self):
        return "<User %s, %s>" % (self.username, self.password)


    async def check_user_in_database(self, connection):
        res = await connection.execute(User.__table__.select().where(User.__table__.c.username==self.username)\
                                                     .where(User.__table__.c.password==self.password).limit(1))
        if res.rowcount == 1:
            row = await res.fetchone()
            return True
        return False

    @classmethod
    def hash_password(cls, password):
        return md5(password.encode('ascii')).hexdigest()




engine = None

if __name__ == '__main__':
    engine = create_engine('postgresql+psycopg2://everjun:password@localhost:5432/test_db')
    Base.metadata.create_all(engine)