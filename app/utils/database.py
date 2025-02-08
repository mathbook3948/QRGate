import bcrypt
from sqlalchemy import create_engine, Column, Integer, DateTime, TEXT, NUMERIC, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship

engine = create_engine("sqlite:///./assets/main.sqlite", echo=True) # 실제로는 이 부분을 database.sqlite로

Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

class User(Base):
    __tablename__ = "user"
    num = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(TEXT, nullable=False)
    user_pwd = Column(TEXT, nullable=False)

def create_table():
    Base.metadata.create_all(engine)

def insert_user(user_id, user_pwd):
    hashed_pwd = bcrypt.hashpw(user_pwd.encode(), bcrypt.gensalt()).decode()
    user = User(user_id=user_id, user_pwd=hashed_pwd)
    session.add(user)
    session.commit()

def select_by_id_user(user_id):
    return session.query(User).filter(User.user_id == user_id).first()


