
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, \
     ForeignKey, event, Table
from sqlalchemy.orm import relationship, scoped_session, sessionmaker, backref, relation
from sqlalchemy.ext.declarative import declarative_base


from flask import url_for
from backend import app

engine = create_engine(app.config['DATABASE_URI'],
                       convert_unicode=True,
                       **app.config['DATABASE_CONNECT_OPTIONS'])
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))



Model = declarative_base(name='Model')
Model.query = db_session.query_property()


def init_db():
    Model.metadata.create_all(bind=engine)

class User(Model):
    __tablename__ = 'user'
    id = Column('user_id', Integer, primary_key=True)
    email = Column('email', String(50), index=True, unique=True)
    name = Column(String(200))
    password = Column(String(500))

    

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = password

    def to_json(self):
        return dict(name=self.name, email=self.email)

    @property
    def is_admin(self):
        return self.openid in app.config['ADMINS']

    def __eq__(self, other):
        return type(self) is type(other) and self.id == other.id

    def __ne__(self, other):
        return not self.__eq__(other)

association_table = Table('association', Model.metadata,
    Column('project_id', Integer, ForeignKey('project.project_id')),
    Column('user_id', Integer, ForeignKey('user.user_id'))
)

class Project(Model):
    __tablename__ = 'project'
    id = Column('project_id', Integer, primary_key=True)
    name = Column(String(50))
    manager_id = Column(Integer, ForeignKey('user.user_id'))
    contributors = relationship("User",
                    secondary=lambda: association_table,
                    backref="projects")

    slug = Column(String(50))

    def __init__(self, name, slug=''):
        self.name = name
        self.slug = '-'.join(name.split()).lower()

    def to_json(self):
        return dict(name=self.name, slug=self.slug)


    @property
    def url(self):
        return url_for('general.projects', slug=self.slug)




