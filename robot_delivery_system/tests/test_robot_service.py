import unittest
from app.database import SessionLocal, engine, Base
from app.services import robot_service, map_service
from app.schemas import RobotCreate, MapCreate

class TestRobotService(unittest.TestCase):
    def setUp(self):
        """Создание тестовой БД перед каждым тестом"""
        Base.metadata.create_all(bind=engine)
        self.db = SessionLocal()
        
        # Создаем тестовую карту
        map_data = MapCreate(name="Test Map", description="Test")
        self.test_map = map_service.create_map(self.db, map_data)

    def tearDown(self):
        """Очистка после каждого теста"""
        self.db.close()
        Base.metadata.drop_all(bind=engine)

    def test_create_robot(self):
        """Тест создания робота"""
        robot_data = RobotCreate(
            name="TestBot-1",
            model="TestModel",
            current_map_id=self.test_map.id
        )
        robot = robot_service.create_robot(self.db, robot_data)
        
        self.assertIsNotNone(robot.id)
        self.assertEqual(robot.name, "TestBot-1")
        self.assertEqual(robot.status, "IDLE")

    def test_get_robot(self):
        """Тест получения робота по ID"""
        robot_data = RobotCreate(
            name="TestBot-2",
            model="TestModel",
            current_map_id=self.test_map.id
        )
        created = robot_service.create_robot(self.db, robot_data)
        fetched = robot_service.get_robot(self.db, created.id)
        
        self.assertEqual(fetched.id, created.id)
        self.assertEqual(fetched.name, "TestBot-2")

    def test_update_robot_status(self):
        """Тест обновления статуса робота"""
        robot_data = RobotCreate(
            name="TestBot-3",
            model="TestModel",
            current_map_id=self.test_map.id
        )
        robot = robot_service.create_robot(self.db, robot_data)
        
        # Обновляем статус
        robot_service.update_robot_status(self.db, robot.id, "BUSY")
        updated = robot_service.get_robot(self.db, robot.id)
        
        self.assertEqual(updated.status, "BUSY")

if __name__ == '__main__':
    unittest.main()