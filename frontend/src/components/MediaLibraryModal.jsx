import React from 'react';

function MediaLibraryModal({ isOpen, onClose, mediaItems, onDownload, onClear }) {
  if (!isOpen) {
    return null;
  }

  return (
    <div id="media-library-modal" className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <header className="modal-header">
          <h2>My Media Library</h2>
          <div className="modal-header-actions">
            <button id="clear-library-button" className="btn btn-secondary" onClick={onClear}>
              <i className="fas fa-trash-alt"></i>
              <span>Clear Library</span>
            </button>
            <button id="modal-close-button" className="btn-icon" onClick={onClose}>&times;</button>
          </div>
        </header>
        <ul id="user-media-list">
          {mediaItems.length === 0 ? (
            <li>Your media library is empty.</li>
          ) : (
            mediaItems.map(item => (
              <li key={item.id} className="media-list-item">
                <div className="media-item-info">
                  <i className={`fas ${item.media_type.startsWith('video') ? 'fa-file-video' : 'fa-file-image'}`}></i>
                  <span>{item.original_filename}</span>
                </div>
                <button
                  className="btn btn-primary download-btn"
                  onClick={() => onDownload(item.id, item.original_filename)}
                >
                  Download
                </button>
              </li>
            ))
          )}
        </ul>
      </div>
    </div>
  );
}

export default MediaLibraryModal;
