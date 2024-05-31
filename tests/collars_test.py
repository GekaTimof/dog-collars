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

class TestRemoveCollar():
    # отвязываем ошейник
    def test_normal_remove_collars(self):
        response = client.post("/collars/remove_collar", json={
              "token": "token2",
              "collar_id": "1"
            })
        assert response.status_code == 200

    # отвязываем ошейник который к нам не привязан
    def test_notown_remove_collars(self):
        response = client.post("/collars/remove_collar", json={
              "token": "token2",
              "collar_id": "2"
            })
        assert response.status_code == 400

    # отвязываем ошейник которого не существует
    def test_notexist_remove_collars(self):
        response = client.post("/collars/remove_collar", json={
              "token": "token2",
              "collar_id": "0"
            })
        assert response.status_code == 400

'''class TestGetMyCollars():
    # получаем ошейники
    def test_normal_get_collars(self):
        response = client.get("/collars/remove_collar", json={
              "token": "token2",
              "collar_id": "1"
            })
        assert response.status_code == 200'''

class TestDeactivateCollar():
    # деактивируем ошейник
    def test_normal_deactivate_collars(self):
        response = client.post("/collars/deactivate_collar", json={
              "token": "token2",
              "collar_id": "4"
            })
        assert response.status_code == 200

    # деактивируем ошейник но без админки
    def test_noadmin_deactivate_collars(self):
        response = client.post("/collars/deactivate_collar", json={
              "token": "token1",
              "collar_id": "5"
            })
        assert response.status_code == 400

    # деактивируем деактивированный ошейник
    def test_unactive_deactivate_collars(self):
        response = client.post("/collars/deactivate_collar", json={
              "token": "token2",
              "collar_id": "3"
            })
        assert response.status_code == 400

class TestActivateCollar():
    # активируем ошейник
    def test_normal_activate_collars(self):
        response = client.post("/collars/activate_collar", json={
              "token": "token2",
              "collar_id": "4"
            })
        assert response.status_code == 200

    # активируем ошейник но без админки
    def test_noadmin_activate_collars(self):
        response = client.post("/collars/activate_collar", json={
              "token": "token1",
              "collar_id": "3"
            })
        assert response.status_code == 400

    # активируем активированный ошейник
    def test_unactive_activate_collars(self):
        response = client.post("/collars/activate_collar", json={
              "token": "token2",
              "collar_id": "5"
            })
        assert response.status_code == 400

class TestPostCoordinates():
    # добавляем координаты ошейника
    def test_normal_post_coords(self):
        response = client.post("/collars/post_coordinates", json={
              "mac": "7590274",
              "coordinates": "43.2 45.78"
            })
        assert response.status_code == 200

    # добавляем координаты ошейника которого не существует
    def test_notexist_post_coords(self):
        response = client.post("/collars/post_coordinates", json={
              "mac": "750000",
              "coordinates": "43.2 45.78"
            })
        assert response.status_code == 400

    # добавляем координаты деактивированного ошейника
    def test_unactive_post_coords(self):
        response = client.post("/collars/post_coordinates", json={
              "mac": "3333",
              "coordinates": "43.2 45.78"
            })
        assert response.status_code == 400


'''class TestOwners():
    # выводим всех владельцев ошейника
    def test_one_owner(self):
        response = client.get("/collars/owners")

        print(response.content)
        assert response.status_code == 200'''