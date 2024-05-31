from conftest import client
class TestAddComplaint():
    # добавление жалобы
    def test_normal_user_registration(self):
        response = client.post("/community/add_complaint", json={
            "token": "token1",
            "user_id": 2,
            "text": "глупи"})

        assert response.status_code == 200