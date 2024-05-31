from conftest import client


class TestRegister():
    # регистрация
    def test_normal_user_registration(self):
        response = client.post("/user/register", json={
            "number": "998",
            "nickname": "test",
            "password": "123",
            "superuser": 1})

        assert response.status_code == 200

    # регистрация по существующему номеру невозможна
    def test_repeated_user_registration(self):
        response = client.post("/user/register", json={
            "number": "89657123459",
            "nickname": "Katya",
            "password": "123",
            "superuser": 1})

        assert response.status_code == 400

    #регистрация с пустым паролем невозможна
    def test_empty_password_registration(self):
        response = client.post("/user/register", json={
            "number": "89657123459",
            "nickname": "Katya",
            "password": "",
            "superuser": 1})

        assert response.status_code == 400

    # регистрация с пустым номером невозможна
    def test_empty_number_registration(self):
        response = client.post("/user/register", json={
            "number": "",
            "nickname": "Katya",
            "password": "",
            "superuser": 1})

        assert response.status_code == 400



class TestAuth():
    # авторизация
    def test_normal_auth(self):
        response = client.post("/user/auth", json={
        "number": "89657123459",
        "password": "890"})

        assert response.status_code == 200

    # авторизация с неверным паролем невозможна
    def test_incorrect_password_auth(self):
        response = client.post("/user/auth", json={
        "number": "88003457826",
        "password": "Dima666"})

        assert response.status_code == 400

    def test_incorrect_user_auth(self):
        response = client.post("/user/auth", json={
        "number": "89657123450",
        "password": "123"})

        assert response.status_code == 400

class TestBan():
    #   админ банит юзера
    def test_normal_ban(self):
        response = client.post("/user/ban", json={
        "token": "token2",
        "user_id": 1})

        assert response.status_code == 200

    # админ банит сам себя
    def test_selfban_ban(self):
        response = client.post("/user/ban", json={
        "token": "token2",
        "user_id": 2})

        assert response.status_code == 200

    # юзер не банит админа
    def test_reverse_ban(self):
        response = client.post("/user/ban", json={
        "token": "token1",
        "user_id": 2})

        assert response.status_code == 400

    # юзер не банит юзера
    def test_selfreverse_ban(self):
        response = client.post("/user/ban", json={
        "token": "token1",
        "user_id": 1})

        assert response.status_code == 400

    # без токена не забанить
    def test_notoken_ban(self):
        response = client.post("/user/ban", json={
        "token": "token0",
        "user_id": 1})

        assert response.status_code == 400

    # банятся только существующие юзеры
    def test_nobody_ban(self):
        response = client.post("/user/ban", json={
        "token": "token2",
        "user_id": 0})

        assert response.status_code == 400


