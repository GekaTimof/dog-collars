from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.orm import declarative_base
import sys

SQLALCHEMY_DATABASE_URL = "sqlite:///./collars.db"

if "pytest" in sys.modules:
    SQLALCHEMY_DATABASE_URL = "sqlite:///./test_collars.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

#SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test_collars.db"

#test_engine = create_engine(
#    SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False}
#)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

DBSession = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

BaseDBModel = declarative_base()
