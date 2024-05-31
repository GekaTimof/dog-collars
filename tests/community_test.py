from conftest import client
class TestAddComplaint():
    # добавление жалобы
    def test_normal_complaint(self):
        response = client.post("/community/add_complaint", json={
            "token": "token1",
            "user_id": 2,
            "text": "глупи"})

        assert response.status_code == 200

    # добавление пустой жалобы
    def test_empty_user_complaint(self):
        response = client.post("/community/add_complaint", json={
            "token": "token1",
            "user_id": 2,
            "text": ""})

        assert response.status_code == 200

    # добавление жалобы на себя
    def test_self_user_complaint(self):
        response = client.post("/community/add_complaint", json={
            "token": "token1",
            "user_id": 1,
            "text": "злой"})

        assert response.status_code == 200

    # добавление жалобы на Женю потому что он меня бесит
    def test_Jenya_user_registration(self):
        response = client.post("/community/add_complaint", json={
            "token": "token2",
            "user_id": 1,
            "text": "не прочитал мои мысли и не понял что я хочу шоколадку((("})

        assert response.status_code == 200

class TestRespondComplaint():
    # жалоба прочитана
    def test_normal_respond_complaint(self):
        response = client.post("/community/respond_complaint", json={
            "token": "token2",
            "complaint_id": 2})

        assert response.status_code == 200

    # прочитанная жалоба прочитана
    def test_again_respond_complaint(self):
        response = client.post("/community/respond_complaint", json={
            "token": "token2",
            "complaint_id": 2})

        assert response.status_code == 400

    # жалоба прочитана без админки
    def test_notadmin_respond_complaint(self):
        response = client.post("/community/respond_complaint", json={
            "token": "token1",
            "complaint_id": 3})

        assert response.status_code == 400

    # жалобы не существует
    def test_nocomplaint_respond_complaint(self):
        response = client.post("/community/respond_complaint", json={
            "token": "token2",
            "complaint_id": 0})

        assert response.status_code == 400


class TestAddTask():
    # добавление задания
    def test_normal_add_task(self):
        response = client.post("/community/add_task", json={
            "token": "token2",
            "collar_id": 2,
            "text": "бегит с собакой",
            "is_alert": False})

        assert response.status_code == 200

    # добавление задания на неактивный ошейник
    def test_unactive_add_task(self):
        response = client.post("/community/add_task", json={
            "token": "token2",
            "collar_id": 3,
            "text": "бегит с собакой",
            "is_alert": False})

        assert response.status_code == 400

    # добавление задания но не админом
    def test_noadmin_add_task(self):
        response = client.post("/community/add_task", json={
            "token": "token1",
            "collar_id": 1,
            "text": "бегит с собакой",
            "is_alert": False})

        assert response.status_code == 400

    # добавление с алертом
    def test_alert_add_task(self):
        response = client.post("/community/add_task", json={
            "token": "token2",
            "collar_id": 1,
            "text": "принести покушать",
            "is_alert": True})

        assert response.status_code == 200

class TestCompleteTask():
    # выполнил задание
    def test_normal_complete_task(self):
        response = client.post("/community/complete_task", json={
            "token": "token1",
            "task_id": 1})

        assert response.status_code == 200

    # выполнил задание но его не существует
    def test_notask_complete_task(self):
        response = client.post("/community/complete_task", json={
            "token": "token1",
            "task_id": 0})

        assert response.status_code == 400

    # выполнил задание которое выполнено
    def test_already_complete_task(self):
        response = client.post("/community/complete_task", json={
            "token": "token2",
            "task_id": 1})

        assert response.status_code == 400