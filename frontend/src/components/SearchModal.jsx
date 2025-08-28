// frontend/src/components/SearchModal.jsx (最終確認版)

import React, { useState, useEffect, useCallback } from 'react';
import apiClient from '../apiClient';

function SearchModal({ initialQuery, isOpen, onClose, onImageSelect, onVideoSelect }) {
  // 這些 state 都屬於 Modal 自己，與 AppView 無關
  const [searchType, setSearchType] = useState('photos');
  const [results, setResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const performSearch = useCallback(async () => {
    if (!initialQuery.trim()) return;
    setIsLoading(true);
    setError(null);
    setResults([]);
    
    try {
      const response = await apiClient.get('/api/pexels/search', {
        params: { query: initialQuery, search_type: searchType }
      });
      setResults(response.data.media);
    } catch (err) {
      setError(err.response?.data?.detail || `Failed to search for ${searchType}.`);
    } finally {
      setIsLoading(false);
    }
  }, [initialQuery, searchType]);

  useEffect(() => {
    if (isOpen) {
      performSearch();
    }
  }, [isOpen, performSearch]);

  if (!isOpen) return null;

  const handleSelect = (item) => {
    if (searchType === 'photos') {
      onImageSelect(item);
    } else {
      onVideoSelect(item);
    }
    onClose();
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content search-modal-content" onClick={(e) => e.stopPropagation()}>
        <header className="modal-header">
          <h2>Search Results for "{initialQuery}"</h2>
          <button className="btn-icon" onClick={onClose}>&times;</button>
        </header>
        <div className="search-type-toggle">
          <button className={`btn ${searchType === 'photos' ? 'btn-primary' : 'btn-secondary'}`} onClick={() => setSearchType('photos')}>Photos</button>
          <button className={`btn ${searchType === 'videos' ? 'btn-primary' : 'btn-secondary'}`} onClick={() => setSearchType('videos')}>Videos</button>
        </div>
        <div className="modal-body">
          {isLoading && <div className="spinner"></div>}
          {error && <p className="error-message">{error}</p>}
          <div className="search-results-grid">
            {searchType === 'photos' ? results.map(photo => (
              <div key={photo.id} className="search-result-item" onClick={() => handleSelect(photo)}>
                <img src={photo.src.medium} alt={photo.alt} />
              </div>
            )) : results.map(video => {
              const thumbnailUrl = video.video_pictures && video.video_pictures.length > 0
                ? video.video_pictures[0].picture
                : null; 
              if (!thumbnailUrl) {
                return null;
              }
              return (
                <div key={video.id} className="search-result-item" onClick={() => handleSelect(video)}>
                  <img src={thumbnailUrl} alt={video.user?.name || 'Pexels Video'} />
                  <div className="video-overlay"><i className="fas fa-play"></i></div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}

export default SearchModal;