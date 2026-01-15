import React, { useState } from 'react';
import { createRequest } from '../services/api';

function RequestForm({ userId, robotId, onRequestCreated }) {
  const [targetX, setTargetX] = useState('');
  const [targetY, setTargetY] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    if (!targetX || !targetY) {
      setError('Заполните все поля');
      setLoading(false);
      return;
    }
    
    try {
      const request = await createRequest(
        userId,
        robotId,
        parseFloat(targetX),
        parseFloat(targetY)
      );
      onRequestCreated(request);
      setTargetX('');
      setTargetY('');
    } catch (err) {
      setError('Ошибка создания заявки');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="request-form">
      <h4>Создать заявку на перемещение</h4>
      <form onSubmit={handleSubmit}>
        <div className="form-row">
          <div className="form-group">
            <label>X:</label>
            <input
              type="number"
              step="0.1"
              value={targetX}
              onChange={(e) => setTargetX(e.target.value)}
              placeholder="0.0"
              required
            />
          </div>
          <div className="form-group">
            <label>Y:</label>
            <input
              type="number"
              step="0.1"
              value={targetY}
              onChange={(e) => setTargetY(e.target.value)}
              placeholder="0.0"
              required
            />
          </div>
        </div>
        {error && <p className="error-message">{error}</p>}
        <button 
          type="submit" 
          className="submit-button"
          disabled={loading}
        >
          {loading ? 'Создание...' : 'Создать заявку'}
        </button>
      </form>
    </div>
  );
}

export default RequestForm;