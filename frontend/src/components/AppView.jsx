import React, { useState, useEffect, useCallback } from 'react';
import apiClient from '../apiClient';
import FilterBar from './FilterBar';
import MediaLibraryModal from './MediaLibraryModal';
import SearchModal from './SearchModal';
import MfaSetupView from './MfaSetupView'; // Import the MFA setup component
import { useAuth } from '../AuthContext'; // Import useAuth

function AppView({ handleLogout }) {
  const { isMfaEnabled, disableMfa } = useAuth(); // Get MFA status and functions
  const [filters, setFilters] = useState([]);
  const [selectedFilterId, setSelectedFilterId] = useState(null);
  const [uiState, setUiState] = useState('initial');
  const [currentFile, setCurrentFile] = useState(null);
  const [downloadUrl, setDownloadUrl] = useState('');
  const [processedFilename, setProcessedFilename] = useState('');
  const [isLibraryOpen, setIsLibraryOpen] = useState(false);
  const [mediaItems, setMediaItems] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [isSearchModalOpen, setIsSearchModalOpen] = useState(false);
  const [isMfaSetupOpen, setIsMfaSetupOpen] = useState(false); // State for MFA setup modal

  // --- ✨ PAGINATION STATE START ✨ ---
  const [currentPage, setCurrentPage] = useState(1);
  const [totalItems, setTotalItems] = useState(0);
  const ITEMS_PER_PAGE = 10; // 和後端 limit 保持一致
  // --- ✨ PAGINATION STATE END ✨ ---

  const handleDisableMfa = async () => {
    if (window.confirm('Are you sure you want to disable Two-Factor Authentication?')) {
      try {
        await disableMfa();
        alert('MFA has been disabled.');
      } catch (error) {
        alert(`Failed to disable MFA: ${error.message}`);
      }
    }
  };

  const fetchFilters = useCallback(async (page) => {
    try {
      // ✨ 向新的分頁 API 發送請求
      const response = await apiClient.get(`/filters/?page=${page}&limit=${ITEMS_PER_PAGE}`);
      setFilters(response.data.items);
      setTotalItems(response.data.total_items);
    } catch (error) { 
      console.error('Failed to fetch filters:', error); 
    }
  }, []);

  // ✨ 當 currentPage 改變時，重新獲取資料
  useEffect(() => { 
    fetchFilters(currentPage); 
  }, [currentPage, fetchFilters]);

  // ✨ 處理分頁變更的函式
  const handlePageChange = (newPage) => {
    if (newPage > 0 && newPage <= Math.ceil(totalItems / ITEMS_PER_PAGE)) {
      setCurrentPage(newPage);
    }
  };

  const handleLutUploadClick = () => { document.getElementById('lut-input').click(); };

  const handleLutFileChange = async (event) => {
    const file = event.target.files[0];
    if (!file || !file.name.endsWith('.cube')) {
      alert('Only .cube LUT files are supported.');
      return;
    }
    try {
      const formData = new FormData();
      formData.append('file', file);
      await apiClient.post('/filters/upload', formData);
      alert('LUT uploaded successfully!');
      // ✨ 上傳成功後回到第一頁並重新獲取資料
      if (currentPage !== 1) {
        setCurrentPage(1);
      } else {
        fetchFilters(1);
      }
    } catch (error) {
      alert(`Failed to upload LUT: ${error.response?.data?.detail || error.message}`);
    } finally {
      event.target.value = '';
    }
  };

  // ... (你其他的函式維持不變) ...
  const resetState = () => {
    setUiState('initial');
    setCurrentFile(null);
    setSelectedFilterId(null);
    setDownloadUrl('');
    setProcessedFilename('');
    const fileInput = document.getElementById('file-input');
    if (fileInput) fileInput.value = '';
  };

  const handleFileSelect = (file) => {
    if (!file) return;
    setCurrentFile(file);
    setUiState('file_selected');
  };

  const handleProcess = async (filterId) => {
    if (!currentFile) return;
    setUiState('processing');
    try {
      const mediaFormData = new FormData();
      mediaFormData.append('file', currentFile);
      const uploadResponse = await apiClient.post('/media/upload', mediaFormData);
      const processResponse = await apiClient.post('/process', {
        media_id: uploadResponse.data.id,
        filter_id: filterId,
      });
      const downloadResponse = await apiClient.get(`/media/download/${processResponse.data.processed_media_id}`, {
        responseType: 'blob',
      });
      const blobUrl = URL.createObjectURL(downloadResponse.data);
      setDownloadUrl(blobUrl);
      setProcessedFilename(processResponse.data.processed_filename);
      setUiState('complete');
    } catch (error) {
      alert(`An error occurred during processing: ${error.response?.data?.detail || error.message}`);
      setUiState('file_selected');
    }
  };

  const handleFilterSelect = (filterId) => {
    setSelectedFilterId(filterId);
    handleProcess(filterId);
  };

  const handleDragOver = (e) => { e.preventDefault(); e.stopPropagation(); };
  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (uiState === 'initial') {
        const files = e.dataTransfer.files;
        if (files && files.length > 0) {
            handleFileSelect(files[0]);
        }
    }
  };

  const handleOpenLibrary = async () => {
    try {
      const response = await apiClient.get('/media/');
      setMediaItems(response.data);
      setIsLibraryOpen(true);
    } catch (error) {
      console.error('Failed to fetch media library:', error);
      alert('Failed to load media library.');
    }
  };

  const handleCloseLibrary = () => {
    setIsLibraryOpen(false);
  };

  const handleDownloadFromLibrary = async (mediaId, filename) => {
    try {
      const response = await apiClient.get(`/media/download/${mediaId}`, {
        responseType: 'blob',
      });
      const url = URL.createObjectURL(response.data);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Download failed:', error);
      alert('Failed to download file.');
    }
  };

  const handleSearch = () => {
    if (searchQuery.trim() !== '') {
      setIsSearchModalOpen(true); // 打開模態視窗
    }
  };

  const handlePexelsImageSelect = async (photo) => {
    setUiState('processing'); // 顯示載入動畫
    
    try {
      // 1. 從 Pexels URL 下載圖片數據
      const response = await fetch(photo.src.original);
      const blob = await response.blob(); // 轉換成 Blob 物件

      // 2. 將 Blob 轉換成 JavaScript 的 File 物件
      const imageFile = new File([blob], `${photo.id}.jpg`, { type: 'image/jpeg' });

      // 3. ✨ 呼叫你現有的 handleFileSelect 函式！ ✨
      // 這樣就無縫接軌到你原本的濾鏡套用流程了
      handleFileSelect(imageFile);

    } catch (error) {
      console.error("Failed to load Pexels image:", error);
      alert("Failed to load the selected image.");
      resetState();
    }
  };

  const handlePexelsVideoSelect = async (video) => {
    setUiState('processing');
    
    try {
      // 找到畫質最好的 mp4 檔案
      const videoFile = video.video_files.find(f => f.quality === 'hd') || video.video_files[0];
      const response = await fetch(videoFile.link);
      const blob = await response.blob();
      
      const videoFileObject = new File([blob], `${video.id}.mp4`, { type: 'video/mp4' });
      
      handleFileSelect(videoFileObject); // ✨ 再次重用你現有的核心流程！

    } catch (error) {
      console.error("Failed to load Pexels video:", error);
      alert("Failed to load the selected video.");
      resetState();
    }
  };
  

  const handleClearLibrary = async () => {
    if (!window.confirm('Are you sure you want to delete your entire media library? This action cannot be undone.')) {
      return;
    }
    try {
      await apiClient.delete('/media/all');
      setMediaItems([]);
    } catch (error) {
      console.error('Failed to clear library:', error);
      alert('Failed to clear your media library.');
    }
  };

  const renderDropZoneContent = () => {


    switch (uiState) {
      case 'file_selected':
        return (
          <div className="state-container">
            <i className="fas fa-file-video"></i>
            <p>Selected File: <strong>{currentFile?.name}</strong></p>
            <button onClick={(e) => { e.stopPropagation(); resetState(); }} className="btn-icon" title="Choose a different file">&times;</button>
          </div>
        );
      case 'processing':
        return (
          <div className="state-container">
            <div className="spinner"></div>
            <h3>Applying Filter</h3>
            <p>Please wait, this may take a moment...</p>
          </div>
        );
      case 'complete':
        return (
          <div className="state-container">
            <i className="fas fa-check-circle"></i>
            <h3>Processing Complete!</h3>
            <a href={downloadUrl} className="btn btn-primary" download={processedFilename}>
              <i className="fas fa-download"></i>
              <span>Download File</span>
            </a>
          </div>
        );
      default:
        return (
          <div className="state-container">
            <i className="fas fa-upload"></i>
            <h3>Click or Drag & Drop to Upload</h3>
            <p>Begin your session by selecting a video or photo</p>
          </div>
        );
    }
  };

  return (
    <div id="app-view" className="view">
      <div className="left-panel">
        <FilterBar
          filters={filters}
          selectedFilterId={selectedFilterId}
          onFilterSelect={handleFilterSelect}
          onLutUploadClick={handleLutUploadClick}
          isActive={uiState === 'file_selected'}
          // --- ✨ PAGINATION PROPS START ✨ ---
          currentPage={currentPage}
          totalItems={totalItems}
          itemsPerPage={ITEMS_PER_PAGE}
          onPageChange={handlePageChange}
          // --- ✨ PAGINATION PROPS END ✨ ---
        />
        <input
          type="file"
          id="lut-input"
          accept=".cube"
          className="hidden"
          onChange={handleLutFileChange}
        />
      </div>
      <div className="right-panel">
        <header className="app-header">
            <button id="media-library-button" className="btn btn-secondary" onClick={handleOpenLibrary}>
              <i className="fas fa-images"></i>
              <span>My Library</span>
            </button>

            <div className="search-container">
              <i className="fas fa-search"></i>
              <input 
                  type="text" 
                  placeholder="Search for photos on Pexels..." 
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyDown={(e) => {
                      if (e.key === 'Enter') {
                          handleSearch(); // 按下 Enter 時呼叫 handleSearch
                      }
                  }}
              />
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
              {isMfaEnabled ? (
                <button onClick={handleDisableMfa} className="btn btn-secondary">
                  <i className="fas fa-shield-alt"></i>
                  <span>Disable MFA</span>
                </button>
              ) : (
                <button onClick={() => setIsMfaSetupOpen(true)} className="btn btn-secondary">
                  <i className="fas fa-shield-alt"></i>
                  <span>Setup MFA</span>
                </button>
              )}

              <button id="logout-button" className="btn btn-secondary" onClick={handleLogout}>
                <i className="fas fa-sign-out-alt"></i>
                <span>Logout</span>
              </button>
            </div>
        </header>

        <main
          id="media-drop-zone"
          onClick={() => uiState === 'initial' && document.getElementById('file-input').click()}
          onDragOver={handleDragOver}
          onDrop={handleDrop}
        >
          {renderDropZoneContent()}
        </main>
        <input
          type="file"
          id="file-input"
          accept="image/*,video/*"
          className="hidden"
          onChange={(e) => handleFileSelect(e.target.files[0])}
        />
      </div>

      {/* Modal for MFA Setup */}
      {isMfaSetupOpen && (
        <div className="modal-overlay">
          <div className="modal-content">
            <MfaSetupView closeView={() => setIsMfaSetupOpen(false)} />
          </div>
        </div>
      )}

      <MediaLibraryModal
        isOpen={isLibraryOpen}
        onClose={handleCloseLibrary}
        mediaItems={mediaItems}
        onDownload={handleDownloadFromLibrary}
        onClear={handleClearLibrary}
      />
      <SearchModal
        isOpen={isSearchModalOpen}
        initialQuery={searchQuery}
        onClose={() => setIsSearchModalOpen(false)}
        onImageSelect={handlePexelsImageSelect} 
        onVideoSelect={handlePexelsVideoSelect}
      />
    </div>
  );
}

export default AppView;
