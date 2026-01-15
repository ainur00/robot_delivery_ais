import time
import requests
import json
import logging
from datetime import datetime
from typing import List, Dict

# Настройки
API_BASE_URL = "http://192.168.56.104/api"
POLL_INTERVAL = 1  # секунды
MOVE_SPEED = 0.005   # метров в секунду (виртуальная скорость)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RobotEmulator:
    def __init__(self):
        self.active_robots = {}  # robot_id -> current_trajectory_info
    
    def get_in_progress_requests(self) -> List[Dict]:
        """Получает IN_PROGRESS заявки"""
        try:
            response = requests.get(f"{API_BASE_URL}/requests/")
            if response.status_code == 200:
                all_requests = response.json()
                in_progress = [r for r in all_requests if r.get("status") == "IN_PROGRESS"]
                return in_progress
        except Exception as e:
            logger.error(f"Ошибка получения заявок: {e}")
        return []
    
    def get_trajectory_for_request(self, request_id: int) -> List[Dict]:
        """Получает траекторию для заявки"""
        try:
            response = requests.get(f"{API_BASE_URL}/trajectories/request/{request_id}")
            if response.status_code == 200:
                trajectory = response.json()
                return self.parse_trajectory(trajectory.get("path_data", ""))
        except Exception as e:
            logger.error(f"Ошибка получения траектории для заявки {request_id}: {e}")
        return []
    
    def parse_trajectory(self, path_string: str) -> List[Dict]:
        """Парсит строку траектории в список точек"""
        if not path_string:
            return []
        
        points = []
        try:
            point_strings = path_string.split(';')
            for point_str in point_strings:
                if not point_str.strip():
                    continue
                    
                point = {}
                pairs = point_str.split(',')
                for pair in pairs:
                    if ':' in pair:
                        key, value = pair.split(':', 1)
                        try:
                            point[key] = float(value)
                        except ValueError:
                            point[key] = value
                
                if 'x' in point and 'y' in point:
                    points.append(point)
            
            logger.debug(f"Распарсено {len(points)} точек траектории")
            
        except Exception as e:
            logger.error(f"Ошибка парсинга траектории: {e}")
        
        return points
    
    def update_robot_position(self, robot_id: int, x: float, y: float) -> bool:
        """Обновляет позицию робота через API"""
        try:
            response = requests.patch(
                f"{API_BASE_URL}/robots/{robot_id}/position?x={x}&y={y}"
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Ошибка обновления позиции робота {robot_id}: {e}")
            return False
    
    def complete_request(self, request_id: int) -> bool:
        """Завершает заявку"""
        try:
            response = requests.patch(f"{API_BASE_URL}/requests/{request_id}/complete")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Ошибка завершения заявки {request_id}: {e}")
            return False
    
    def process_robot_movement(self, robot_id: int, trajectory: List[Dict]):
        """Обрабатывает движение робота по траектории"""
        if not trajectory:
            logger.error(f"Нет траектории для робота {robot_id}")
            return
        
        logger.info(f"Робот {robot_id} начинает движение по траектории ({len(trajectory)} точек)")
        
        # Двигаемся по точкам траектории
        for i, point in enumerate(trajectory):
            x = point.get('x', 0)
            y = point.get('y', 0)
            
            # Обновляем позицию
            if self.update_robot_position(robot_id, x, y):
                logger.debug(f"Робот {robot_id} -> точка {i+1}/{len(trajectory)}: ({x:.2f}, {y:.2f})")
            
            # Задержка для имитации движения
            time.sleep(MOVE_SPEED)
        
        logger.info(f"Робот {robot_id} завершил движение")
    
    def process_request(self, request: Dict):
        """Обрабатывает одну IN_PROGRESS заявку"""
        request_id = request.get("id")
        robot_id = request.get("robot_id")
        
        logger.info(f"Обработка IN_PROGRESS заявки {request_id} для робота {robot_id}")
        
        # Получаем траекторию
        trajectory = self.get_trajectory_for_request(request_id)
        
        if not trajectory:
            logger.error(f"Нет траектории для заявки {request_id}")
            return
        
        # Запускаем движение робота
        self.process_robot_movement(robot_id, trajectory)
        
        # Завершаем заявку
        if self.complete_request(request_id):
            logger.info(f"Заявка {request_id} завершена (COMPLETED)")
        else:
            logger.error(f"Не удалось завершить заявку {request_id}")
    
    def run(self):
        """Основной цикл эмулятора"""
        logger.info("Эмулятор роботов запущен")
        logger.info(f"Скорость движения: {MOVE_SPEED} м/с")
        
        while True:
            try:
                # Получаем IN_PROGRESS заявки
                in_progress_requests = self.get_in_progress_requests()
                
                if in_progress_requests:
                    logger.info(f"Найдено {len(in_progress_requests)} IN_PROGRESS заявок")
                    
                    # Обрабатываем каждую заявку
                    for request in in_progress_requests:
                        # Проверяем, не обрабатывается ли уже этот робот
                        robot_id = request.get("robot_id")
                        if robot_id not in self.active_robots:
                            self.active_robots[robot_id] = request
                            self.process_request(request)
                            del self.active_robots[robot_id]
                        else:
                            logger.debug(f"Робот {robot_id} уже в обработке")
                else:
                    logger.debug("Нет IN_PROGRESS заявок")
                
                # Ждем перед следующей проверкой
                time.sleep(POLL_INTERVAL)
                
            except KeyboardInterrupt:
                logger.info("Эмулятор остановлен")
                break
            except Exception as e:
                logger.error(f"Ошибка в основном цикле: {e}")
                time.sleep(POLL_INTERVAL)

def main():
    emulator = RobotEmulator()
    emulator.run()

if __name__ == "__main__":
    main()