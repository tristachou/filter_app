// frontend/src/components/SearchModal.jsx (新檔案)

import React, { useState, useEffect } from 'react';
import apiClient from '../apiClient';

function SearchModal({ initialQuery, isOpen, onClose, onImageSelect }) {
  const [query, setQuery] = useState(initialQuery);
  const [results, setResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // useEffect 會在模態視窗打開時，自動執行搜尋
  useEffect(() => {
    if (isOpen && initialQuery.trim() !== '') {
      const performSearch = async () => {
        setIsLoading(true);
        setError(null);
        try {
          const response = await apiClient.get(`/api/pexels/search`, {
            params: { query: initialQuery }
          });
          setResults(response.data.photos);
        } catch (err) {
          setError(err.response?.data?.detail || 'Failed to search for images.');
        } finally {
          setIsLoading(false);
        }
      };
      performSearch();
    }
  }, [isOpen, initialQuery]); // 依賴項：當 isOpen 或 initialQuery 變化時觸發

  if (!isOpen) {
    return null; // 如果模態是關閉的，就什麼都不渲染
  }

  const handleSelect = (photo) => {
    onImageSelect(photo); // 呼叫父元件傳來的函式
    onClose(); // 選擇後自動關閉
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content search-modal-content" onClick={(e) => e.stopPropagation()}>
        <header className="modal-header">
          <h2>Search Results for "{initialQuery}"</h2>
          <button className="btn-icon" onClick={onClose}>&times;</button>
        </header>
        
        <div className="modal-body">
          {isLoading && <div className="spinner"></div>}
          {error && <p className="error-message">{error}</p>}
          {!isLoading && !error && (
            <div className="search-results-grid">
              {results.map(photo => (
                <div key={photo.id} className="search-result-item" onClick={() => handleSelect(photo)}>
                  <img src={photo.src.medium} alt={photo.alt} />
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default SearchModal;