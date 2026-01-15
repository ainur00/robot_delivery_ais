import React, { useEffect, useState } from 'react';
import { getRobotMapImage } from '../services/api';

function MapLoader({ robotId, onMapLoaded }) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const loadMap = async () => {
      if (!robotId) return;
      
      setLoading(true);
      setError('');
      
      try {
        const imageBlob = await getRobotMapImage(robotId);
        const imageUrl = URL.createObjectURL(imageBlob);
        
        const img = new Image();
        
        img.onload = () => {
          onMapLoaded({
            image: img,
            width: img.width,
            height: img.height
          });
          setLoading(false);
        };
        
        img.onerror = () => {
          setError('Не удалось загрузить изображение карты');
          setLoading(false);
        };
        
        img.src = imageUrl;
        
      } catch (err) {
        console.error('Ошибка загрузки карты:', err);
        setError(`Ошибка: ${err.message}`);
        setLoading(false);
      }
    };
    
    loadMap();
  }, [robotId, onMapLoaded]);
  
  if (loading) return <div className="loading">Загрузка карты...</div>;
  if (error) return <div className="error">{error}</div>;
  
  return null;
}

export default MapLoader;