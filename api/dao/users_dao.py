from api.models import User

from api.dao.base_dao import BasedDAO


class UsersDAO(BasedDAO):
    model = User
