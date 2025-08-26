document.addEventListener('DOMContentLoaded', () => {

  // ========================================================================
  // 1. API CLIENT
  // ========================================================================
  // A centralized place to handle all API requests.
  // It automatically adds the JWT token to the headers.

  const apiClient = axios.create({
    baseURL: 'http://localhost:8000', // Make sure this matches your backend!
  });

  apiClient.interceptors.request.use((config) => {
    const token = localStorage.getItem('jwt_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  }, (error) => {
    return Promise.reject(error);
  });


  // ========================================================================
  // 2. APPLICATION STATE & MODULES
  // ========================================================================
  // The main App object holds the application's state and initializes modules.

  const App = {
    token: null,
    isLibraryOpen: false,
    isLoading: false,

    init() {
      console.log('App initializing...');
      this.token = localStorage.getItem('jwt_token');
      
      if (this.token) {
        this.showAppView();
      } else {
        this.showLoginView();
      }
      
      LoginModule.init();
      AppModule.init(); // Initialize the main app module
    },

    showLoginView() {
      document.getElementById('login-view').classList.remove('hidden');
      document.getElementById('app-view').classList.add('hidden');
    },

    showAppView() {
      document.getElementById('login-view').classList.add('hidden');
      document.getElementById('app-view').classList.remove('hidden');
      // When showing the app view, we should fetch the filters
      AppModule.FilterBarModule.fetchFilters();
    },

    loginSuccess(token) {
      this.token = token;
      localStorage.setItem('jwt_token', token);
      this.showAppView();
    },

    logout() {
      this.token = null;
      localStorage.removeItem('jwt_token');
      this.showLoginView();
    }
  };


  // ========================================================================
  // 3. LOGIN MODULE
  // ========================================================================
  // Handles all logic related to the login form.

  const LoginModule = {
    init() {
      const loginForm = document.getElementById('login-form');
      if (loginForm) {
        loginForm.addEventListener('submit', this.handleLogin.bind(this));
      }
    },

    async handleLogin(e) {
      e.preventDefault();
      const username = e.target.username.value;
      const password = e.target.password.value;
      const errorEl = document.getElementById('login-error');
      errorEl.textContent = '';

      try {
        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);

        const response = await apiClient.post('/api/auth/token', formData);
        App.loginSuccess(response.data.access_token);

      } catch (error) {
        errorEl.textContent = 'Invalid credentials. Please try again.';
        console.error('Login failed:', error);
      }
    }
  };


  // ========================================================================
  // 4. APP MODULE (Main application logic after login)
  // ========================================================================
  // This module will contain all the sub-modules for the main app view.

  const AppModule = {
    init() {
      this.HeaderModule.init();
      this.FilterBarModule.init();
      this.MediaUploadModule.init();
      this.MediaLibraryModule.init();

      const lutInput = document.getElementById('lut-input');
      if (lutInput) {
        lutInput.addEventListener('change', (e) => this.handleLutUpload(e.target.files[0]));
      }
      const uploadFilterBox = document.getElementById('upload-filter-box');
      if (uploadFilterBox && lutInput) {
        uploadFilterBox.addEventListener('click', () => {
          lutInput.click();
        });
      }
    },

    async handleLutUpload(file) {
      if (!file) return;
      if (!file.name.endsWith('.cube')) {
        alert('Only .cube LUT files are supported.');
        return;
      }

      App.isLoading = true;
      try {
        const formData = new FormData();
        formData.append('file', file);

        await apiClient.post('/api/filters/upload', formData);
        alert('LUT uploaded successfully!');
        // Re-fetch filters to update the list with the new LUT
        this.FilterBarModule.fetchFilters();
      } catch (error) {
        console.error('LUT upload failed:', error);
        alert(`Failed to upload LUT: ${error.response?.data?.detail || error.message}`);
      } finally {
        App.isLoading = false;
        // Clear the file input to allow re-uploading the same file
        document.getElementById('lut-input').value = '';
      }
    },

    // --- Header Sub-Module ---
    HeaderModule: {
      init() {
        const logoutButton = document.getElementById('logout-button');
        if (logoutButton) {
          logoutButton.addEventListener('click', () => App.logout());
        }
        const mediaLibraryButton = document.getElementById('media-library-button');
        if (mediaLibraryButton) {
          mediaLibraryButton.addEventListener('click', () => AppModule.MediaLibraryModule.open());
        }
      }
    },

    // --- Filter Bar Sub-Module ---
    FilterBarModule: {
      filters: [],
      init() {
        const filterListEl = document.getElementById('preset-filter-list');
        if (filterListEl) {
          filterListEl.addEventListener('click', (e) => {
            const swatch = e.target.closest('.filter-swatch');
            if (swatch && swatch.dataset.filterId) {
              // Deselect others
              document.querySelectorAll('.filter-swatch.selected').forEach(s => s.classList.remove('selected'));
              // Select clicked one
              swatch.classList.add('selected');
              // Notify the MediaUploadModule to start processing
              AppModule.MediaUploadModule.startProcessing(swatch.dataset.filterId);
            }
          });
        }
      },
      async fetchFilters() {
        try {
          const response = await apiClient.get('/api/filters/');
          this.filters = response.data;
          this.renderFilters();
        } catch (error) {
          console.error('Failed to fetch filters:', error);
          alert('Could not load filters. Please try refreshing the page.');
        }
      },
      renderFilters() {
        const filterListEl = document.getElementById('preset-filter-list');
        filterListEl.innerHTML = ''; // Clear existing filters
        this.filters.forEach(filter => {
          const swatch = document.createElement('div');
          swatch.className = 'filter-swatch';
          // Use the correct property name from the backend (which we fixed earlier)
          swatch.innerHTML = `<span>${filter.filter_name || filter.name}</span>`; 
          swatch.dataset.filterId = filter.id;
          filterListEl.appendChild(swatch);
        });
      }
    },

    // --- Media Upload Sub-Module ---
    MediaUploadModule: {
      currentFile: null,
      init() {
        const dropZone = document.getElementById('media-drop-zone');
        const fileInput = document.getElementById('file-input');
        const cancelBtn = document.getElementById('cancel-selection-button');

        dropZone.addEventListener('click', () => fileInput.click());
        fileInput.addEventListener('change', (e) => this.handleFileSelect(e.target.files[0]));
        cancelBtn.addEventListener('click', (e) => {
          e.stopPropagation();
          this.setUIState('initial');
        });

        // Drag and Drop listeners
        dropZone.addEventListener('dragover', (e) => {
          e.preventDefault();
          e.stopPropagation();
          dropZone.classList.add('active-drop');
        });
        dropZone.addEventListener('dragleave', (e) => {
          e.preventDefault();
          e.stopPropagation();
          dropZone.classList.remove('active-drop');
        });
        dropZone.addEventListener('drop', (e) => {
          e.preventDefault();
          e.stopPropagation();
          dropZone.classList.remove('active-drop');
          this.handleFileSelect(e.dataTransfer.files[0]);
        });
      },

      handleFileSelect(file) {
        if (!file) return;
        this.currentFile = file;
        document.getElementById('selected-filename').textContent = file.name;
        this.setUIState('file_selected');
      },

      async startProcessing(filterId) {
        if (!this.currentFile) {
          alert('Please select a media file first.');
          return;
        }
        this.setUIState('processing');

        try {
          // 1. Upload the media file
          const mediaFormData = new FormData();
          mediaFormData.append('file', this.currentFile);
          const uploadResponse = await apiClient.post('/api/media/upload', mediaFormData);

          // 2. Start the processing job
          const processResponse = await apiClient.post('/api/process', {
            media_id: uploadResponse.data.id,
            filter_id: filterId,
          });

          // 3. Download the result
          const downloadResponse = await apiClient.get(`/api/media/download/${processResponse.data.processed_media_id}`, {
            responseType: 'blob',
          });
          const blob = downloadResponse.data;
          
          const downloadLink = document.getElementById('download-link');
          const blobUrl = URL.createObjectURL(blob);

          // Remove old listeners to prevent duplicates
          const newDownloadLink = downloadLink.cloneNode(true);
          downloadLink.parentNode.replaceChild(newDownloadLink, downloadLink);

          newDownloadLink.href = blobUrl;
          newDownloadLink.download = processResponse.data.processed_filename;

          newDownloadLink.addEventListener('click', (e) => {
            // We handle the click manually to have more control
            e.preventDefault();
            // Create a temporary link to trigger the download
            const tempLink = document.createElement('a');
            tempLink.href = blobUrl;
            tempLink.download = processResponse.data.processed_filename;
            document.body.appendChild(tempLink);
            tempLink.click();
            document.body.removeChild(tempLink);

            // After download, reset the UI to the initial state
            this.setUIState('initial');
          });

          this.setUIState('complete');

        } catch (error) {
          console.error('Processing failed:', error);
          alert(`An error occurred during processing: ${error.response?.data?.detail || error.message}`);
          this.setUIState('file_selected'); // Revert to file selected state
        }
      },

      setUIState(state) {
        const states = {
          initial: document.getElementById('upload-prompt'),
          file_selected: document.getElementById('file-info'),
          processing: document.getElementById('processing-state'),
          complete: document.getElementById('result-state'),
        };

        // Hide all states
        Object.values(states).forEach(el => el.classList.add('hidden'));
        // Show the target state
        if (states[state]) {
          states[state].classList.remove('hidden');
        }

        // Also manage the filter bar state
        const filterBar = document.getElementById('filter-bar');
        if (state === 'file_selected') {
          filterBar.classList.add('active');
        } else {
          filterBar.classList.remove('active');
        }

        if (state === 'initial') {
          this.currentFile = null;
          document.getElementById('file-input').value = '';
        }
      }
    },

    // --- Media Library Sub-Module ---
    MediaLibraryModule: {
      isOpen: false,
      mediaItems: [],
      init() {
        const openBtn = document.getElementById('media-library-button');
        const closeBtn = document.getElementById('modal-close-button');
        const modalOverlay = document.getElementById('media-library-modal');
        const listEl = document.getElementById('user-media-list');
        const clearBtn = document.getElementById('clear-library-button');

        openBtn.addEventListener('click', () => this.open());
        closeBtn.addEventListener('click', () => this.close());
        modalOverlay.addEventListener('click', (e) => {
          if (e.target === modalOverlay) {
            this.close();
          }
        });

        listEl.addEventListener('click', (e) => {
          const downloadBtn = e.target.closest('.download-btn');
          if (downloadBtn) {
            e.preventDefault();
            const mediaId = downloadBtn.dataset.mediaId;
            const filename = downloadBtn.dataset.filename;
            this.handleDownload(mediaId, filename);
          }
        });

        clearBtn.addEventListener('click', () => this.handleClear());
      },

      async open() {
        this.isOpen = true;
        document.getElementById('media-library-modal').classList.remove('hidden');
        await this.fetchMedia();
      },

      close() {
        this.isOpen = false;
        document.getElementById('media-library-modal').classList.add('hidden');
      },

      async fetchMedia() {
        const listEl = document.getElementById('user-media-list');
        listEl.innerHTML = '<li>Loading...</li>'; // Show loading indicator
        try {
          const response = await apiClient.get('/api/media/');
          this.mediaItems = response.data;
          this.renderMedia();
        } catch (error) {
          console.error('Failed to fetch media library:', error);
          listEl.innerHTML = '<li>Failed to load library.</li>';
        }
      },

      renderMedia() {
        const listEl = document.getElementById('user-media-list');
        listEl.innerHTML = '';

        if (this.mediaItems.length === 0) {
          listEl.innerHTML = '<li>Your media library is empty.</li>';
          return;
        }

        this.mediaItems.forEach(item => {
          const li = document.createElement('li');
          li.className = 'media-list-item';
          li.innerHTML = `
            <div class="media-item-info">
              <i class="fas ${item.media_type.startsWith('video') ? 'fa-file-video' : 'fa-file-image'}"></i>
              <span>${item.original_filename}</span>
            </div>
            <a href="#" class="btn btn-primary download-btn" data-media-id="${item.id}" data-filename="${item.original_filename}">Download</a>
          `;
          listEl.appendChild(li);
        });
      },

      async handleDownload(mediaId, filename) {
        try {
          const response = await apiClient.get(`/api/media/download/${mediaId}`, {
            responseType: 'blob',
          });
          const blob = response.data;
          const url = URL.createObjectURL(blob);
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
      },

      async handleClear() {
        if (!confirm('Are you sure you want to delete your entire media library? This action cannot be undone.')) {
          return;
        }
        try {
          await apiClient.delete('/api/media/all');
          this.mediaItems = [];
          this.renderMedia();
        } catch (error) {
          console.error('Failed to clear library:', error);
          alert('Failed to clear your media library.');
        }
      }
    }
  };


  // ========================================================================
  // 5. INITIALIZE THE APP
  // ========================================================================
  App.init();

});