from locust import HttpUser, task, between, tag
import random

class RobotDeliveryUser(HttpUser):
    """Минимальный тест: только GET-запросы"""
    wait_time = between(1, 3)  # Ждем 1-3 секунды между запросами
    
    @tag("get_robots")
    @task(5)  # Самый частый запрос
    def get_all_robots(self):
        """GET /robots/ - получение списка роботов"""
        with self.client.get("/robots/", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status: {response.status_code}")
    
    @tag("get_available")
    @task(3)
    def get_available_robots(self):
        """GET /robots/available - доступные роботы"""
        with self.client.get("/robots/available", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status: {response.status_code}")
    
    # @tag("get_user_requests")
    # @task(2)
    # def get_user_requests(self):
    #     """GET /requests/user/{id} - заявки пользователя"""
    #     with self.client.get(f"/requests/user/{random.randint(1, 1000)}", catch_response=True) as response:
    #         if response.status_code == 200:
    #             response.success()
    #         else:
    #             response.failure(f"Status: {response.status_code}")
    
    # @tag("create_request")
    # @task(1)
    # def create_and_complete_request(self):
    #     """Создать заявку и сразу завершить её (цикл)"""
    #     data = {
    #         "user_id": random.randint(1, 1000),
    #         "robot_id": random.randint(1, 1000),
    #         "target_x": random.uniform(0, 100),
    #         "target_y": random.uniform(0, 100)
    #     }
        
    #     # 1. Создаем заявку
    #     with self.client.post("/requests/", json=data, catch_response=True) as response:
    #         if response.status_code in [201, 400]:
    #             response.success()
    #         else:
    #             response.failure(f"Status: {response.status_code}")