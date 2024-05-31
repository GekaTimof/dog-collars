from conftest import client


class TestRegister():
    def test_normal_user_registration(self):
        response = client.post("/user/register", json={
            "number": "998",
            "nickname": "test",
            "password": "123",
            "superuser": 1})

        assert response.status_code == 200

    def test_repeated_user_registration(self):
        response = client.post("/user/register", json={
            "number": "89657123459",
            "nickname": "Katya",
            "password": "123",
            "superuser": 1})

        assert response.status_code == 400

    def test_empty_password_registration(self):
        response = client.post("/user/register", json={
            "number": "89657123459",
            "nickname": "Katya",
            "password": "",
            "superuser": 1})

        assert response.status_code == 400


class TestAuth():
    '''def test_normal_auth(self):
        response = client.post("/user/auth", json={
        "number": "89657123459",
        "password": "098"})

        assert response.status_code == 200'''

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

'''class TestBan():
    def test_normal_ban(self):
        response = client.post("/user/ban", json={
        "token": "56a2a257-173f-4ba7-bbf4-fd35f1498f15",
        "user_id": 1})

        assert response.status_code == 200'''

