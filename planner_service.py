import time
import requests
import json
from typing import Dict, List, Tuple
import logging
from datetime import datetime

# Настройки
API_BASE_URL = "http://192.168.56.104/api"
POLL_INTERVAL = 2  # секунды

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Заглушка для функции расчета пути (замени на свою)
def get_path(start_x: float, start_y: float, end_x: float, end_y: float) -> List[Dict[str, float]]:
    """
    Генерирует простую траекторию от старта до цели.
    В реальности здесь будет вызов твоего алгоритма планирования.
    """
    logger.info(f"Расчёт пути из ({start_x}, {start_y}) в ({end_x}, {end_y})")
    
    # Простая линейная интерполяция (10 точек)
    points = []
    num_points = 10
    
    for i in range(num_points + 1):
        t = i / num_points
        x = start_x + (end_x - start_x) * t
        y = start_y + (end_y - start_y) * t
        
        # Добавляем параметры для робота (v, th, de, a, w можно настроить)
        point = {
            "x": round(x, 2),
            "y": round(y, 2),
            "v": 1.0,  # скорость
            "th": 0.0,  # угол
            "de": 0.0,  # угол поворота колес
            "a": 0.0,   # ускорение
            "w": 0.0    # угловая скорость
        }
        points.append(point)
    
    logger.info(f"Сгенерировано {len(points)} точек траектории")
    return points

def points_to_path_string(points: List[Dict[str, float]]) -> str:
    """Преобразует список точек в строку формата API"""
    path_parts = []
    for point in points:
        point_parts = [f"{key}:{value}" for key, value in point.items()]
        path_parts.append(",".join(point_parts))
    
    return ";".join(path_parts)

def get_pending_requests() -> List[Dict]:
    """Получает список PENDING заявок"""
    try:
        response = requests.get(f"{API_BASE_URL}/requests/")
        if response.status_code == 200:
            all_requests = response.json()
            pending_requests = [r for r in all_requests if r.get("status") == "PENDING"]
            return pending_requests
    except Exception as e:
        logger.error(f"Ошибка получения заявок: {e}")
    return []

def get_robot_position(robot_id: int) -> Tuple[float, float]:
    """Получает текущую позицию робота"""
    try:
        response = requests.get(f"{API_BASE_URL}/robots/{robot_id}")
        if response.status_code == 200:
            robot = response.json()
            x = robot.get("current_position_x", 0.0)
            y = robot.get("current_position_y", 0.0)
            return float(x), float(y)
    except Exception as e:
        logger.error(f"Ошибка получения позиции робота {robot_id}: {e}")
    return 0.0, 0.0

def update_request_status(request_id: int, status: str) -> bool:
    """Обновляет статус заявки"""
    try:
        response = requests.patch(
            f"{API_BASE_URL}/requests/{request_id}/status?status={status}"
        )
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Ошибка обновления статуса заявки {request_id}: {e}")
        return False

def create_trajectory(request_id: int, path_data: str) -> bool:
    """Создает запись траектории"""
    try:
        trajectory_data = {
            "request_id": request_id,
            "path_data": path_data
        }
        
        response = requests.post(
            f"{API_BASE_URL}/trajectories/",
            json=trajectory_data
        )
        
        if response.status_code == 200:
            logger.info(f"Траектория создана для заявки {request_id}")
            return True
        else:
            logger.error(f"Ошибка создания траектории: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"Ошибка создания траектории для заявки {request_id}: {e}")
        return False

def process_request(request: Dict):
    """Обрабатывает одну PENDING заявку"""
    request_id = request.get("id")
    robot_id = request.get("robot_id")
    target_x = request.get("target_x")
    target_y = request.get("target_y")
    
    logger.info(f"Обработка заявки {request_id}: робот {robot_id} -> ({target_x}, {target_y})")
    
    # 1. Меняем статус на PLANNING
    if not update_request_status(request_id, "PLANNING"):
        logger.error(f"Не удалось обновить статус заявки {request_id}")
        return
    
    # 2. Получаем текущую позицию робота
    start_x, start_y = get_robot_position(robot_id)
    logger.info(f"Робот {robot_id} сейчас на позиции ({start_x}, {start_y})")
    
    # 3. Рассчитываем траекторию (используем твою функцию get_path)
    try:
        # points = get_path(start_x, start_y, target_x, target_y)
        # Или если твоя функция возвращает другой формат:
        points = get_path(start_x, start_y, float(target_x), float(target_y))
        
        # 4. Преобразуем в строку
        path_string = points_to_path_string(points)
        
        # 5. Создаем траекторию в БД
        if create_trajectory(request_id, path_string):
            # 6. Меняем статус на READY
            update_request_status(request_id, "READY")
            logger.info(f"Заявка {request_id} готова (статус: READY)")
        else:
            logger.error(f"Не удалось создать траекторию для заявки {request_id}")
            update_request_status(request_id, "FAILED")
            
    except Exception as e:
        logger.error(f"Ошибка расчета траектории для заявки {request_id}: {e}")
        update_request_status(request_id, "FAILED")

def main():
    """Основной цикл планировщика"""
    logger.info("Планировщик траекторий запущен")
    logger.info(f"Опрашиваем API: {API_BASE_URL}")
    
    while True:
        try:
            # Получаем PENDING заявки
            pending_requests = get_pending_requests()
            
            if pending_requests:
                logger.info(f"Найдено {len(pending_requests)} PENDING заявок")
                
                # Обрабатываем каждую заявку
                for request in pending_requests:
                    process_request(request)
                    time.sleep(0.5)  # Небольшая пауза между обработкой
            else:
                logger.debug("Нет PENDING заявок")
            
            # Ждем перед следующей проверкой
            time.sleep(POLL_INTERVAL)
            
        except KeyboardInterrupt:
            logger.info("Планировщик остановлен")
            break
        except Exception as e:
            logger.error(f"Ошибка в основном цикле: {e}")
            time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    main()