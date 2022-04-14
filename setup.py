from base import Session
import os
import glob


def session_dec(func):
    '''
    decorator for methods working with SqlAlchemy database.
    Creates new session before and commits it after changes are applied.

    :param func:
    '''

    def wraper(*args, **kwargs):
        session = Session()
        func(session=session, *args, **kwargs)
        session.commit()
        session.close()
    return wraper
