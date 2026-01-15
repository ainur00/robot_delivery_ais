import React, { useState, useEffect } from 'react';
import './App.css';
import Login from './components/Login';
import RobotList from './components/RobotList';
import RobotMap from './components/RobotMap';
import RequestForm from './components/RequestForm';
import TrajectoryViewer from './components/TrajectoryViewer';
import { login, getRobotById, updateRobotCoordinates } from './services/api';

function App() {
  const [user, setUser] = useState(null);
  const [selectedRobotId, setSelectedRobotId] = useState(null);
  const [robotData, setRobotData] = useState(null);
  const [currentRequest, setCurrentRequest] = useState(null);
  const [targetPoint, setTargetPoint] = useState(null);
  const [trajectoryPoints, setTrajectoryPoints] = useState([]);
  
  // Периодическое обновление координат робота
  useEffect(() => {
    if (!selectedRobotId) return;
    
    const updateCoordinates = async () => {
      try {
        const coords = await updateRobotCoordinates(selectedRobotId);
        setRobotData(prev => prev ? {
          ...prev,
          current_position_x: coords.current_position_x,
          current_position_y: coords.current_position_y
        } : null);
        
        console.log('Обновлены координаты:', coords);
      } catch (error) {
        console.error('Ошибка обновления координат:', error);
      }
    };
    
    // Первое обновление сразу
    updateCoordinates();
    
    // Затем каждые 5 секунд
    const interval = setInterval(updateCoordinates, 5000);
    return () => clearInterval(interval);
  }, [selectedRobotId]);

  const handleLogin = (userData) => {
    setUser(userData);
  };

  const handleSelectRobot = async (robotId) => {
    setSelectedRobotId(robotId);
    
    try {
      const robotData = await getRobotById(robotId);
      console.log('Загружены данные робота:', robotData);
      setRobotData(robotData);
    } catch (error) {
      console.error('Ошибка загрузки робота:', error);
      setRobotData({
        id: robotId,
        name: `Робот-${robotId}`,
        status: 'IDLE',
        current_position_x: 0,
        current_position_y: 0,
      });
    }
  };

  const handleRequestCreated = (request) => {
    setCurrentRequest(request);
    setTargetPoint({ x: request.target_x, y: request.target_y });
    // НЕ создаём фейковую траекторию - ждём реальную
    setTrajectoryPoints([]);
  };

  const handleAccept = () => {
    // alert('Заявка принята! Робот начал движение.');
  };

  const handleReject = () => {
    // alert('Заявка отклонена.');
  };

  const handleTrajectoryCompleted = () => {
    console.log('Очищаем траекторию (заявка завершена)');
    setTrajectoryPoints([]);
    setCurrentRequest(null);
    setTargetPoint(null);
  };

  if (!user) {
    return (
      <div className="App">
        <header className="app-header">
          <h1>Система управления автономными роботами-доставщиками</h1>
        </header>
        <Login onLogin={handleLogin} />
      </div>
    );
  }

  return (
    <div className="App">
      <header className="app-header">
        <h1>Система управления автономными роботами-доставщиками</h1>
        <div className="user-info">
          Вы вошли как: <strong>{user.username}</strong> (ID: {user.id})
        </div>
      </header>
      
      <div className="app-container">
        <div className="sidebar">
          <RobotList onSelectRobot={handleSelectRobot} />
          
          {selectedRobotId && (
            <>
              <RequestForm
                userId={user.id}
                robotId={selectedRobotId}
                onRequestCreated={handleRequestCreated}
              />
              
              {currentRequest && (
                <TrajectoryViewer
                  requestId={currentRequest.id}
                  onAccept={handleAccept}
                  onReject={handleReject}
                  onTrajectoryLoaded={(points) => setTrajectoryPoints(points)}
                />
              )}
            </>
          )}
        </div>
        
        <div className="main-content">
          <RobotMap
            robot={robotData}
            targetPoint={targetPoint}
            trajectoryPoints={trajectoryPoints}
            robotId={selectedRobotId}
          />
        </div>
      </div>
    </div>
  );
}

export default App;