import React from 'react';

function DebugPanel({ robot, trajectoryPoints, targetPoint }) {
  if (!robot) return null;
  
  return (
    <div className="debug-panel">
      <h4>Отладка</h4>
      <div className="debug-section">
        <h5>Робот:</h5>
        <pre>{JSON.stringify({
          id: robot.id,
          name: robot.name,
          status: robot.status,
          position_x: robot.current_position_x,
          position_y: robot.current_position_y,
          hasPosition: robot.current_position_x !== undefined && robot.current_position_y !== undefined
        }, null, 2)}</pre>
      </div>
      
      {trajectoryPoints && trajectoryPoints.length > 0 && (
        <div className="debug-section">
          <h5>Траектория ({trajectoryPoints.length} точек):</h5>
          <pre>{JSON.stringify(trajectoryPoints.slice(0, 3), null, 2)}</pre>
          {trajectoryPoints.length > 3 && <p>... и ещё {trajectoryPoints.length - 3} точек</p>}
        </div>
      )}
      
      {targetPoint && (
        <div className="debug-section">
          <h5>Цель:</h5>
          <pre>{JSON.stringify(targetPoint, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}

export default DebugPanel;