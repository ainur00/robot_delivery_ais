import React, { useEffect, useRef, useState } from 'react';
import MapLoader from './MapLoader';
import DebugPanel from './DebugPanel';

function RobotMap({ robot, targetPoint, trajectoryPoints, robotId }) {
  const canvasRef = useRef(null);
  const [mapData, setMapData] = useState(null);
  const [debugMode, setDebugMode] = useState(true);
  
  // Функция преобразования координат (ОЧЕНЬ ВАЖНАЯ!)
  const worldToCanvas = (worldX, worldY, mapData, canvas) => {
    if (!mapData || !canvas) return { x: 0, y: 0 };
    
    const mapWidth = mapData.width;
    const mapHeight = mapData.height;
    
    // Масштаб для отображения всей карты
    const scaleX = canvas.width / mapWidth;
    const scaleY = canvas.height / mapHeight;
    const scale = Math.min(scaleX, scaleY) * 0.85; // 85% от размера
    
    const displayWidth = mapWidth * scale;
    const displayHeight = mapHeight * scale;
    const offsetX = (canvas.width - displayWidth) / 2;
    const offsetY = (canvas.height - displayHeight) / 2;
    
    // Преобразование: левый нижний угол карты = (0, 0)
    const canvasX = offsetX + (worldX * scale);
    // Инвертируем Y: в мире Y растёт вверх, на канвасе Y растёт вниз
    const canvasY = canvas.height - (offsetY + (worldY * scale));
    
    return { x: canvasX, y: canvasY };
  };
  
  // Отрисовка карты
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || !mapData) return;
    
    const ctx = canvas.getContext('2d');
    
    // ОЧИСТКА КАНВАСА
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // 1. ФОН
    ctx.fillStyle = '#0a1929';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    const mapWidth = mapData.width;
    const mapHeight = mapData.height;
    
    // Масштаб
    const scaleX = canvas.width / mapWidth;
    const scaleY = canvas.height / mapHeight;
    const scale = Math.min(scaleX, scaleY) * 0.85;
    const displayWidth = mapWidth * scale;
    const displayHeight = mapHeight * scale;
    const offsetX = (canvas.width - displayWidth) / 2;
    const offsetY = (canvas.height - displayHeight) / 2;
    
    // 2. РИСУЕМ КАРТУ
    if (mapData.image) {
      ctx.drawImage(mapData.image, offsetX, offsetY, displayWidth, displayHeight);
      
      // Обводка карты
      ctx.strokeStyle = '#00ff00';
      ctx.lineWidth = 2;
      ctx.strokeRect(offsetX, offsetY, displayWidth, displayHeight);
    }
    
    // 3. КООРДИНАТНАЯ СЕТКА (каждые 10 метров)
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.2)';
    ctx.lineWidth = 1;
    ctx.font = '10px Arial';
    ctx.fillStyle = 'white';
    
    for (let x = 0; x <= mapWidth; x += 10) {
      const canvasX = offsetX + (x * scale);
      ctx.beginPath();
      ctx.moveTo(canvasX, offsetY);
      ctx.lineTo(canvasX, offsetY + displayHeight);
      ctx.stroke();
      
      if (x % 20 === 0) {
        ctx.fillText(`${x}`, canvasX - 5, offsetY + displayHeight + 15);
      }
    }
    
    for (let y = 0; y <= mapHeight; y += 10) {
      const canvasY = canvas.height - (offsetY + (y * scale));
      ctx.beginPath();
      ctx.moveTo(offsetX, canvasY);
      ctx.lineTo(offsetX + displayWidth, canvasY);
      ctx.stroke();
      
      if (y % 20 === 0) {
        ctx.fillText(`${y}`, offsetX - 25, canvasY + 3);
      }
    }
    
    // 4. ОСИ КООРДИНАТ
    ctx.strokeStyle = 'white';
    ctx.lineWidth = 2;
    
    // Ось X
    ctx.beginPath();
    ctx.moveTo(offsetX, canvas.height - offsetY);
    ctx.lineTo(offsetX + displayWidth, canvas.height - offsetY);
    ctx.stroke();
    
    // Ось Y
    ctx.beginPath();
    ctx.moveTo(offsetX, canvas.height - offsetY);
    ctx.lineTo(offsetX, canvas.height - offsetY - displayHeight);
    ctx.stroke();
    
    // 5. ТОЧКА РОБОТА (САМАЯ ВАЖНАЯ ЧАСТЬ!)
    if (robot && robot.current_position_x !== undefined && robot.current_position_y !== undefined) {
      const robotX = parseFloat(robot.current_position_x) || 0;
      const robotY = parseFloat(robot.current_position_y) || 0;
      
      console.log('РОБОТ координаты:', { 
        robotX, 
        robotY,
        raw: { x: robot.current_position_x, y: robot.current_position_y }
      });
      
      const robotPos = worldToCanvas(robotX, robotY, mapData, canvas);
      
      console.log('РОБОТ на канвасе:', robotPos);
      
      // Большой синий круг (робот)
      ctx.fillStyle = '#2196F3';
      ctx.beginPath();
      ctx.arc(robotPos.x, robotPos.y, 20, 0, Math.PI * 2);
      ctx.fill();
      
      // Белая обводка
      ctx.strokeStyle = 'white';
      ctx.lineWidth = 3;
      ctx.stroke();
      
      // Жёлтая обводка внутри
      ctx.strokeStyle = '#FFEB3B';
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.arc(robotPos.x, robotPos.y, 15, 0, Math.PI * 2);
      ctx.stroke();
      
      // Иконка робота
      ctx.fillStyle = 'white';
      ctx.font = 'bold 24px Arial';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText('🤖', robotPos.x, robotPos.y);
      
      // Подпись "Робот"
      ctx.font = 'bold 14px Arial';
      ctx.fillStyle = '#2196F3';
      ctx.fillText(`Робот "${robot.name}"`, robotPos.x, robotPos.y + 35);
      
      // Координаты под роботом
      ctx.font = '12px Arial';
      ctx.fillStyle = 'white';
      ctx.fillText(`X:${robotX.toFixed(1)} Y:${robotY.toFixed(1)}`, robotPos.x, robotPos.y + 50);
      
      // Красный маркер в центре робота
      ctx.fillStyle = '#ff0000';
      ctx.beginPath();
      ctx.arc(robotPos.x, robotPos.y, 3, 0, Math.PI * 2);
      ctx.fill();
    } else {
      console.log('РОБОТ: нет координат', robot);
    }
    
    // 6. ТРАЕКТОРИЯ (если есть)
    if (trajectoryPoints && trajectoryPoints.length > 0) {
      console.log('Траектория точек:', trajectoryPoints.length);
      
      // Фильтруем валидные точки
      const validPoints = trajectoryPoints.filter(
        point => point && typeof point.x === 'number' && typeof point.y === 'number'
      );
      
      console.log('Валидных точек:', validPoints.length);
      
      if (validPoints.length > 0) {
        // Линия траектории (толстая зелёная)
        ctx.strokeStyle = '#00FF00';
        ctx.lineWidth = 4;
        ctx.lineJoin = 'round';
        ctx.lineCap = 'round';
        
        ctx.beginPath();
        
        validPoints.forEach((point, index) => {
          const canvasPoint = worldToCanvas(point.x, point.y, mapData, canvas);
          
          if (index === 0) {
            ctx.moveTo(canvasPoint.x, canvasPoint.y);
          } else {
            ctx.lineTo(canvasPoint.x, canvasPoint.y);
          }
        });
        
        ctx.stroke();
        
        // Точки траектории (цветные круги)
        validPoints.forEach((point, index) => {
          const canvasPoint = worldToCanvas(point.x, point.y, mapData, canvas);
          
          // Цвет в зависимости от позиции
          let color;
          let radius = 8;
          
          if (index === 0) {
            color = '#2196F3'; // Начало - синий
            radius = 10;
          } else if (index === validPoints.length - 1) {
            color = '#FF5722'; // Конец - оранжевый
            radius = 10;
          } else {
            color = '#4CAF50'; // Промежуточные - зелёный
            radius = 6;
          }
          
          // Круг
          ctx.fillStyle = color;
          ctx.beginPath();
          ctx.arc(canvasPoint.x, canvasPoint.y, radius, 0, Math.PI * 2);
          ctx.fill();
          
          // Белая обводка
          ctx.strokeStyle = 'white';
          ctx.lineWidth = 2;
          ctx.stroke();
          
          // Номер точки (первые 20)
          if (index < 20) {
            ctx.fillStyle = 'white';
            ctx.font = 'bold 10px Arial';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText(`${index + 1}`, canvasPoint.x, canvasPoint.y);
          }
        });
        
        // Подпись траектории
        if (validPoints.length >= 2) {
          const start = worldToCanvas(validPoints[0].x, validPoints[0].y, mapData, canvas);
          const end = worldToCanvas(
            validPoints[validPoints.length - 1].x, 
            validPoints[validPoints.length - 1].y, 
            mapData, 
            canvas
          );
          
          ctx.fillStyle = '#00FF00';
          ctx.font = 'bold 16px Arial';
          ctx.fillText('ТРАЕКТОРИЯ', canvas.width / 2, 30);
          
          ctx.font = '12px Arial';
          ctx.fillText(
            `Начало: (${validPoints[0].x.toFixed(1)}, ${validPoints[0].y.toFixed(1)}) → ` +
            `Конец: (${validPoints[validPoints.length - 1].x.toFixed(1)}, ${validPoints[validPoints.length - 1].y.toFixed(1)})`,
            canvas.width / 2,
            50
          );
        }
      }
    }
    
    // 7. ЦЕЛЕВАЯ ТОЧКА (если есть и нет траектории)
    if (targetPoint && (!trajectoryPoints || trajectoryPoints.length === 0)) {
      const targetPos = worldToCanvas(targetPoint.x, targetPoint.y, mapData, canvas);
      
      // Большой красный круг
      ctx.fillStyle = '#FF0000';
      ctx.beginPath();
      ctx.arc(targetPos.x, targetPos.y, 15, 0, Math.PI * 2);
      ctx.fill();
      
      // Белая обводка
      ctx.strokeStyle = 'white';
      ctx.lineWidth = 3;
      ctx.stroke();
      
      // Чёрный крестик
      ctx.strokeStyle = 'black';
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(targetPos.x - 8, targetPos.y - 8);
      ctx.lineTo(targetPos.x + 8, targetPos.y + 8);
      ctx.moveTo(targetPos.x + 8, targetPos.y - 8);
      ctx.lineTo(targetPos.x - 8, targetPos.y + 8);
      ctx.stroke();
      
      // Подпись "Цель"
      ctx.fillStyle = '#FF0000';
      ctx.font = 'bold 14px Arial';
      ctx.fillText(`Цель`, targetPos.x, targetPos.y + 30);
    }
    
    // 8. ЛЕГЕНДА
    /*
    ctx.fillStyle = 'rgba(0, 0, 0, 0.8)';
    ctx.fillRect(20, 20, 200, 160);
    
    ctx.fillStyle = 'white';
    ctx.font = 'bold 16px Arial';
    ctx.fillText('ЛЕГЕНДА', 30, 45);
    
    ctx.font = '14px Arial';
    
    // Робот
    ctx.fillStyle = '#2196F3';
    ctx.beginPath();
    ctx.arc(30, 70, 8, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = 'white';
    ctx.fillText('Робот', 45, 73);
    
    // Траектория
    ctx.strokeStyle = '#00FF00';
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(30, 90);
    ctx.lineTo(50, 90);
    ctx.stroke();
    ctx.fillStyle = 'white';
    ctx.fillText('Траектория', 55, 93);
    
    // Начало
    ctx.fillStyle = '#2196F3';
    ctx.beginPath();
    ctx.arc(30, 115, 6, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = 'white';
    ctx.fillText('Начало', 45, 118);
    
    // Конец
    ctx.fillStyle = '#FF5722';
    ctx.beginPath();
    ctx.arc(30, 140, 6, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = 'white';
    ctx.fillText('Конец', 45, 143);
    */

    // 9. ИНФОРМАЦИЯ О КАРТЕ
    ctx.fillStyle = 'rgba(0, 0, 0, 0.8)';
    ctx.fillRect(canvas.width - 250, 20, 230, 70);
    
    ctx.fillStyle = 'white';
    ctx.font = 'bold 16px Arial';
    ctx.textAlign = 'right';
    ctx.fillText('КАРТА', canvas.width - 30, 45);
    
    ctx.font = '14px Arial';
    ctx.textAlign = 'left';
    ctx.fillText(`Размер: ${mapWidth} × ${mapHeight} м`, canvas.width - 240, 45);
    ctx.fillText(`1 пиксель = 1 метр`, canvas.width - 240, 70);
    
  }, [mapData, robot, targetPoint, trajectoryPoints]);
  
  return (
    <div className="robot-map-container">
      <div className="map-header">
        <h2>Карта робота {robot?.name || 'не выбран'}</h2>
        <button 
          onClick={() => setDebugMode(!debugMode)}
          className="debug-toggle"
        >
          {debugMode ? 'Скрыть отладку' : 'Показать отладку'}
        </button>
      </div>
      
      {robotId && <MapLoader robotId={robotId} onMapLoaded={setMapData} />}
      
      <div className="map-wrapper">
        <canvas 
          ref={canvasRef} 
          width={1200} 
          height={800}
          className="map-canvas"
        />
      </div>
      
      {debugMode && (
        <DebugPanel 
          robot={robot}
          trajectoryPoints={trajectoryPoints}
          targetPoint={targetPoint}
        />
      )}
      
      <div className="coordinates-info">
        {robot && (
          <div className="coordinate-item">
            <strong>Робот "{robot.name}":</strong> 
            X = <span className="coord-value">{(robot.current_position_x || 0).toFixed(2)}</span> м, 
            Y = <span className="coord-value">{(robot.current_position_y || 0).toFixed(2)}</span> м
          </div>
        )}
        {trajectoryPoints && trajectoryPoints.length > 0 && (
          <div className="coordinate-item">
            <strong>Траектория:</strong> {trajectoryPoints.length} точек
          </div>
        )}
      </div>
    </div>
  );
}

export default RobotMap;