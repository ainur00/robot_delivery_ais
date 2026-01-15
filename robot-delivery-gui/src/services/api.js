import axios from 'axios';

const API_BASE = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const login = async (username, password) => {
  const response = await api.post('/users/login', { username, password });
  return response.data;
};

export const getRobots = async () => {
  const response = await api.get('/robots/');
  return response.data;
};

export const getRobotById = async (id) => {
  const response = await api.get(`/robots/${id}`);
  return response.data;
};

export const createRequest = async (user_id, robot_id, target_x, target_y) => {
  const response = await api.post('/requests/', {
    user_id,
    robot_id,
    target_x,
    target_y,
  });
  return response.data;
};

export const getTrajectoryByRequestId = async (request_id) => {
  const response = await api.get(`/trajectories/request/${request_id}`);
  return response.data;
};

export const acceptRequest = async (request_id) => {
  const response = await api.patch(`/requests/${request_id}/accept`);
  return response.data;
};

export const rejectRequest = async (request_id) => {
  const response = await api.patch(`/requests/${request_id}/reject`);
  return response.data;
};

export const getRobotMapPath = async (robot_id) => {
  const response = await api.get(`/robots/${robot_id}/map`);
  return response.data;
};

// Обновить позицию робота (для эмуляции движения)
export const updateRobotPosition = async (robot_id, x, y) => {
  const response = await api.patch(`/robots/${robot_id}/position?x=${x}&y=${y}`);
  return response.data;
};

// Занять робота (сделать BUSY)
export const occupyRobot = async (robot_id) => {
  const response = await api.patch(`/robots/${robot_id}/occupy`);
  return response.data;
};

// Получить доступных роботов
export const getAvailableRobots = async () => {
  const response = await api.get('/robots/available');
  return response.data;
};

export const getRobotMapImage = async (robot_id) => {
  const response = await api.get(`/robots/${robot_id}/map/image`, {
    responseType: 'blob' // Важно для получения файла
  });
  return response.data;
};

export const getRobotPosition = async (robot_id) => {
  try {
    const response = await api.get(`/robots/${robot_id}/position`);
    return response.data;
  } catch (error) {
    console.error('Ошибка получения координат:', error);
    // Если нет отдельного эндпоинта, получаем общую информацию
    const robot = await getRobotById(robot_id);
    return {
      current_position_x: robot.current_position_x,
      current_position_y: robot.current_position_y
    };
  }
};

// Функция для обновления координат робота
export const updateRobotCoordinates = async (robot_id) => {
  try {
    const response = await api.get(`/robots/${robot_id}`);
    return {
      current_position_x: response.data.current_position_x,
      current_position_y: response.data.current_position_y
    };
  } catch (error) {
    console.error('Ошибка обновления координат:', error);
    return { current_position_x: 0, current_position_y: 0 };
  }
};

// Получить заявку по ID
export const getRequestById = async (request_id) => {
  const response = await api.get(`/requests/${request_id}`);
  return response.data;
};

// Обновить статус заявки
export const updateRequestStatus = async (request_id, status) => {
  const response = await api.patch(`/requests/${request_id}/status?status=${status}`);
  return response.data;
};

// Получить все заявки пользователя
export const getUserRequests = async (user_id) => {
  const response = await api.get(`/requests/user/${user_id}`);
  return response.data;
};

export default api;