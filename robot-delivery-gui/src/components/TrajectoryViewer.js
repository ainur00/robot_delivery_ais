import React, { useEffect, useState, useRef } from 'react';
import { 
  getTrajectoryByRequestId, 
  acceptRequest, 
  rejectRequest,
  getRequestById 
} from '../services/api';

function TrajectoryViewer({ requestId, onAccept, onReject, onTrajectoryLoaded }) {
  const [trajectory, setTrajectory] = useState(null);
  const [requestStatus, setRequestStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [hasTrajectory, setHasTrajectory] = useState(false);
  
  // Используем ref для отслеживания, чтобы избежать лишних рендеров
  const trajectoryLoadedRef = useRef(false);
  const pollingIntervalRef = useRef(null);

  // Функция для загрузки статуса заявки
  const loadRequestStatus = async () => {
    try {
      const requestData = await getRequestById(requestId);
      const newStatus = requestData.status;
      
      // Обновляем статус только если он изменился
      if (newStatus !== requestStatus) {
        setRequestStatus(newStatus);
      }
      
      // Если заявка завершена - очищаем траекторию и останавливаем опрос
      if (newStatus === 'COMPLETED' || newStatus === 'FAILED') {
        console.log('Заявка завершена, очищаем траекторию и останавливаем опрос');
        setTrajectory(null);
        setHasTrajectory(false);
        if (onTrajectoryLoaded) {
          onTrajectoryLoaded([]); // Очищаем точки на карте
        }
        
        // Останавливаем опрос
        if (pollingIntervalRef.current) {
          clearInterval(pollingIntervalRef.current);
          pollingIntervalRef.current = null;
        }
        return true; // Возвращаем true чтобы остановить дальнейшую загрузку
      }
      return false;
    } catch (err) {
      console.error('Ошибка загрузки статуса:', err);
      return false;
    }
  };

  // Функция для загрузки траектории (вызывается только один раз при появлении)
  const loadTrajectoryOnce = async () => {
    // Если уже загрузили траекторию или она есть - выходим
    if (trajectoryLoadedRef.current || hasTrajectory) {
      return;
    }
    
    try {
      const data = await getTrajectoryByRequestId(requestId);
      
      // Если получили траекторию
      if (data && data.path_data) {
        console.log('Получена траектория:', data);
        setTrajectory(data);
        setHasTrajectory(true);
        trajectoryLoadedRef.current = true;
        setError('');
        
        // Парсим и отправляем точки
        const points = parsePathData(data.path_data);
        if (points.length > 0 && onTrajectoryLoaded) {
          console.log('Отправляем точки на карту:', points.length);
          onTrajectoryLoaded(points);
        }
        
        // Останавливаем опрос траектории (теперь опрашиваем только статус)
        setLoading(false);
        return true;
      }
    } catch (err) {
      // Если траектория не найдена - это нормально на первых попытках
      if (err.response && err.response.status === 404) {
        setError('Траектория ещё не рассчитана. Ожидайте...');
      } else {
        setError(`Ошибка загрузки: ${err.message}`);
      }
    }
    return false;
  };

  // Основной эффект для начальной загрузки
  useEffect(() => {
    if (!requestId) return;
    
    console.log('Начинаем загрузку данных для заявки:', requestId);
    
    // Сбрасываем флаги при смене requestId
    trajectoryLoadedRef.current = false;
    setHasTrajectory(false);
    setLoading(true);
    setTrajectory(null);
    
    const initialLoad = async () => {
      // 1. Загружаем статус заявки
      const isCompleted = await loadRequestStatus();
      
      // 2. Если заявка не завершена - пытаемся загрузить траекторию
      if (!isCompleted) {
        const hasTraj = await loadTrajectoryOnce();
        
        // 3. Если траектории ещё нет, запускаем интервал для её поиска
        if (!hasTraj) {
          console.log('Траектории нет, запускаем интервал поиска');
          
          // Интервал для поиска траектории (каждые 2 секунды, максимум 30 раз = 1 минута)
          let attempts = 0;
          const maxAttempts = 30;
          
          const trajectoryPolling = setInterval(async () => {
            attempts++;
            
            // Пытаемся загрузить траекторию
            const loaded = await loadTrajectoryOnce();
            
            // Если загрузили или превысили попытки - останавливаем
            if (loaded || attempts >= maxAttempts) {
              clearInterval(trajectoryPolling);
              if (attempts >= maxAttempts) {
                setError('Траектория не была рассчитана в течение минуты');
                setLoading(false);
              }
            }
          }, 2000);
          
          // Сохраняем ID интервала для очистки
          pollingIntervalRef.current = trajectoryPolling;
        }
      } else {
        // Если заявка уже завершена - останавливаем загрузку
        setLoading(false);
      }
    };
    
    initialLoad();
    
    // Интервал для обновления статуса (каждые 5 секунд)
    const statusInterval = setInterval(() => {
      loadRequestStatus();
    }, 5000);
    
    // Очистка при размонтировании
    return () => {
      clearInterval(statusInterval);
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
        pollingIntervalRef.current = null;
      }
    };
  }, [requestId]); // Зависимость только от requestId

  const parsePathData = (pathString) => {
    if (!pathString || typeof pathString !== 'string') return [];
    
    try {
      return pathString.split(';')
        .filter(pointStr => pointStr.trim() !== '')
        .map(pointStr => {
          const point = {};
          pointStr.split(',').forEach(pair => {
            const [key, value] = pair.split(':');
            if (key === 'x' || key === 'y') {
              point[key] = parseFloat(value);
            }
          });
          return point;
        })
        .filter(point => point.x !== undefined && point.y !== undefined);
    } catch (err) {
      console.error('Ошибка парсинга:', err, 'Строка:', pathString);
      return [];
    }
  };

  const handleAccept = async () => {
    try {
      await acceptRequest(requestId);
      alert('Заявка принята! Робот начал движение.');
      onAccept && onAccept();
    } catch (err) {
      setError(`Ошибка принятия: ${err.message}`);
    }
  };

  const handleReject = async () => {
    try {
      await rejectRequest(requestId);
      alert('Заявка отклонена.');
      onReject && onReject();
    } catch (err) {
      setError(`Ошибка отклонения: ${err.message}`);
    }
  };

  const handleDownload = () => {
    if (!trajectory?.path_data) return;
    
    const blob = new Blob([trajectory.path_data], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `trajectory_${requestId}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  // Если заявка завершена - показываем сообщение
  if (requestStatus === 'COMPLETED' || requestStatus === 'FAILED') {
    return (
      <div className="trajectory-container completed">
        <div className="status-icon">
          {requestStatus === 'COMPLETED' ? '✅' : '❌'}
        </div>
        <h4>{requestStatus === 'COMPLETED' ? 'Заявка выполнена' : 'Заявка отклонена'}</h4>
        <p>
          {requestStatus === 'COMPLETED' 
            ? 'Робот успешно достиг цели. Траектория скрыта.'
            : 'Заявка была отклонена. Траектория скрыта.'
          }
        </p>
        <div className="completed-actions">
          <button 
            onClick={() => {
              if (onAccept) onAccept();
            }} 
            className="btn btn-primary"
          >
            Создать новую заявку
          </button>
        </div>
      </div>
    );
  }

  // Показываем загрузку только если нет траектории и нет ошибки
  if (loading && !hasTrajectory && !error) {
    return (
      <div className="trajectory-container loading">
        <div className="spinner"></div>
        <p>⏳ Поиск траектории...</p>
        <p className="loading-subtext">Может занять до 1 минуты</p>
      </div>
    );
  }

  // Если есть ошибка и нет траектории
  if (error && !hasTrajectory) {
    return (
      <div className="trajectory-container waiting">
        <p>{error}</p>
        <p>Траектория появится автоматически после расчёта.</p>
        <button 
          onClick={() => {
            setLoading(true);
            setError('');
            loadTrajectoryOnce();
          }} 
          className="btn btn-retry"
        >
          Попробовать снова
        </button>
      </div>
    );
  }

  // Если траектория загружена - показываем её
  if (hasTrajectory && trajectory) {
    const points = parsePathData(trajectory.path_data);
    
    return (
      <div className="trajectory-container">
        <div className="trajectory-header">
          <h4>Предложенная траектория</h4>
          <div className="status-badge">
            Статус: <span className={`status ${requestStatus?.toLowerCase()}`}>
              {requestStatus || 'Ожидание...'}
            </span>
          </div>
          <div className="trajectory-actions">
            <button onClick={handleDownload} className="btn btn-download" title="Скачать файл траектории">
              Скачать
            </button>
            <button onClick={handleAccept} className="btn btn-accept" title="Принять траекторию">
              Принять
            </button>
            <button onClick={handleReject} className="btn btn-reject" title="Отклонить траекторию">
              Отклонить
            </button>
          </div>
        </div>
        
        <div className="trajectory-info">
          <div className="info-item">
            <strong>ID заявки:</strong> {requestId}
          </div>
          <div className="info-item">
            <strong>Точек в траектории:</strong> {points.length}
          </div>
          <div className="info-item">
            <strong>Рассчитано:</strong> {new Date(trajectory.calculated_at).toLocaleString()}
          </div>
          <div className="info-item">
            <strong>Статус заявки:</strong> 
            <span className={`status-badge ${requestStatus?.toLowerCase()}`}>
              {requestStatus || 'Ожидание...'}
            </span>
          </div>
        </div>
        
        {points.length > 0 && (
          <div className="trajectory-preview">
            <h5>Предпросмотр точек (первые 5):</h5>
            <div className="points-grid">
              {points.slice(0, 5).map((point, idx) => (
                <div key={idx} className="point-card">
                  <div className="point-number">{idx + 1}</div>
                  <div className="point-coordinates">
                    <div>X: <span className="coord-value">{point.x.toFixed(2)}</span></div>
                    <div>Y: <span className="coord-value">{point.y.toFixed(2)}</span></div>
                  </div>
                </div>
              ))}
              {points.length > 5 && (
                <div className="more-points-card">
                  <div className="more-text">... и ещё</div>
                  <div className="more-count">{points.length - 5}</div>
                  <div className="more-text">точек</div>
                </div>
              )}
            </div>
          </div>
        )}
        
        <div className="trajectory-raw">
          <h5>Исходные данные (первые 200 символов):</h5>
          <div className="raw-data">
            {trajectory.path_data?.substring(0, 200)}
            {trajectory.path_data?.length > 200 && '...'}
          </div>
        </div>
        
        {error && (
          <div className="error-message">
            {error}
          </div>
        )}
      </div>
    );
  }

  // Запасной вариант (не должно сюда попадать)
  return (
    <div className="trajectory-container empty">
      <p>Состояние не определено</p>
      <button onClick={() => window.location.reload()}>Обновить страницу</button>
    </div>
  );
}

export default TrajectoryViewer;