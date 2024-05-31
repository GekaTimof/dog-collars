from conftest import client

class TestNewCollar():
    # админ добавляет ошейник
    def test_normal_new_collar(self):
        response = client.post("/collars/new_collar",
        json={
              "token": "token2",
              "mac": "1234"
            })

        assert response.status_code == 200

    # юзер не добавляет ошейник
    def test_user_new_collar(self):
        response = client.post("/collars/new_collar",
        json={
              "token": "token1",
              "mac": "1234"
             })

        assert response.status_code == 400

    # добавление существующего активного ошейника
    def test_old_collar(self):
        response = client.post("/collars/new_collar",
        json={
              "token": "token2",
              "mac": "7590274"
             })

        assert response.status_code == 400

    # добавление существующего неактивного ошейника
    def test_unactive_collar(self):
        response = client.post("/collars/new_collar",
        json={
              "token": "token2",
              "mac": "379574"
             })
        assert response.status_code == 200

    # ошейник не добавляется без токена
    def test_noone_collar(self):
        response = client.post("/collars/new_collar",
        json={
              "token": "",
              "mac": "274"
             })

        assert response.status_code == 400

class TestAddCollar():
    # привязываем ошейник
    def test_normal_add_collars(self):
        response = client.post("/collars/add_collars", json={
              "token": "token1",
              "collar_id": "1"
            })
        assert response.status_code == 200

    # привязываем неактивный ошейник
    def test_unactive_add_collars(self):
        response = client.post("/collars/add_collars", json={
              "token": "token1",
              "collar_id": "3"
            })
        assert response.status_code == 400

    # привязываем ошейник с неверным токеном
    def test_nouser_add_collars(self):
        response = client.post("/collars/add_collars", json={
              "token": "token0",
              "collar_id": "1"
            })
        assert response.status_code == 400

    # привязываем ошейник который уже привязан
    def test_already_add_collars(self):
        response = client.post("/collars/add_collars", json={
              "token": "token2",
              "collar_id": "1"
            })
        assert response.status_code == 400

    # привязываем несуществующий ошейник
    def test_nocollar_add_collars(self):
        response = client.post("/collars/add_collars", json={
              "token": "token2",
              "collar_id": "0"
            })
        assert response.status_code == 400

'''class TestOwners():
    # выводим всех владельцев ошейника
    def test_one_owner(self):
        response = client.get("/collars/owners")

        print(response.content)
        assert response.status_code == 200'''