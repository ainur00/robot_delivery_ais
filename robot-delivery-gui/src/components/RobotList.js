import React, { useEffect, useState } from 'react';
import { getRobots } from '../services/api';

function RobotList({ onSelectRobot }) {
  const [robots, setRobots] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchRobots = async () => {
      try {
        const data = await getRobots();
        setRobots(data);
      } catch (err) {
        setError('Ошибка загрузки роботов');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchRobots();
  }, []);

  if (loading) return <div className="loading">Загрузка роботов...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <div className="robot-list">
      <h3>Список роботов</h3>
      <div className="robot-grid">
        {robots.map((robot) => (
          <div key={robot.id} className="robot-card">
            <div className="robot-info">
              <strong>{robot.name}</strong>
              <span className={`status ${robot.status.toLowerCase()}`}>
                {robot.status}
              </span>
            </div>
            <button 
              onClick={() => onSelectRobot(robot.id)}
              className="select-button"
            >
              Выбрать
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}

export default RobotList;