document.addEventListener('DOMContentLoaded', () => {

    // --- CONFIGURATION & STATE ---
    const API_BASE_URL = 'http://localhost:8000'; // IMPORTANT: Make sure this matches your Python backend!
    let currentMediaFile = null;
    let jwtToken = null;

    // --- DOM ELEMENT SELECTORS ---
    const loginView = document.getElementById('login-view');
    const appView = document.getElementById('app-view');
    const loginForm = document.getElementById('login-form');
    const loginError = document.getElementById('login-error');
    const logoutButton = document.getElementById('logout-button');
    
    const mediaDropZone = document.getElementById('media-drop-zone');
    const uploadPrompt = document.getElementById('upload-prompt');
    const fileInfo = document.getElementById('file-info');
    const processingState = document.getElementById('processing-state');
    const resultState = document.getElementById('result-state');
    const selectedFilenameSpan = document.getElementById('selected-filename');
    const cancelSelectionButton = document.getElementById('cancel-selection-button');
    
    const fileInput = document.getElementById('file-input');
    const filterBar = document.getElementById('filter-bar');
    const presetFilterList = document.getElementById('preset-filter-list');
    const uploadLutBox = document.getElementById('upload-filter-box');
    const lutInput = document.getElementById('lut-input');
    
    const downloadLink = document.getElementById('download-link');
    
    const mediaLibraryButton = document.getElementById('media-library-button');
    const modal = document.getElementById('media-library-modal');
    const modalCloseButton = document.getElementById('modal-close-button');
    const userMediaList = document.getElementById('user-media-list');
    const clearLibraryButton = document.getElementById('clear-library-button');

    // --- STATE MANAGEMENT ---
    const updateUIState = (state) => {
        const states = { initial: uploadPrompt, file_selected: fileInfo, processing: processingState, complete: resultState };
        Object.values(states).forEach(el => el.classList.add('hidden'));
        if (states[state]) states[state].classList.remove('hidden');

        if (state === 'initial') {
            mediaDropZone.classList.add('active-drop');
            filterBar.classList.remove('active');
            currentMediaFile = null;
            fileInput.value = '';
        } else if (state === 'file_selected') {
            mediaDropZone.classList.remove('active-drop');
            filterBar.classList.add('active');
        } else {
            mediaDropZone.classList.remove('active-drop');
            filterBar.classList.remove('active');
        }
    };

    // --- API HELPER ---
    const apiRequest = async (endpoint, options = {}) => {
        const headers = { 'Authorization': `Bearer ${jwtToken}`, ...options.headers };
        const response = await fetch(`${API_BASE_URL}${endpoint}`, { ...options, headers });
        if (response.status === 401) { handleLogout(); throw new Error('Session expired.'); }
        if (!response.ok) {
            const err = await response.json().catch(() => ({ detail: 'An unknown error occurred' }));
            throw new Error(err.detail);
        }
        if (options.responseType === 'blob') return response.blob();
        return response.json();
    };

    // --- CORE LOGIC ---
    const initializeApp = async () => {
        loginView.classList.add('hidden');
        appView.classList.remove('hidden');
        updateUIState('initial');
        await fetchAndRenderFilters();
    };

    const handleLogin = async (e) => {
        e.preventDefault();
        loginError.textContent = '';
        const data = new URLSearchParams({ username: e.target.username.value, password: e.target.password.value });
        try {
            const response = await fetch(`${API_BASE_URL}/api/auth/token`, { method: 'POST', body: data });
            if (!response.ok) throw new Error('Invalid credentials');
            const { access_token } = await response.json();
            jwtToken = access_token;
            localStorage.setItem('jwt_token', jwtToken);
            initializeApp();
        } catch (error) {
            loginError.textContent = error.message;
        }
    };
    
    const handleLogout = () => {
        localStorage.removeItem('jwt_token');
        jwtToken = null;
        appView.classList.add('hidden');
        loginView.classList.remove('hidden');
    };

    const handleFileSelect = (file) => {
        if (!file) return;
        currentMediaFile = file;
        selectedFilenameSpan.textContent = file.name;
        updateUIState('file_selected');
    };

    const fetchAndRenderFilters = async () => {
        try {
            const filters = await apiRequest('/api/filters/');
            presetFilterList.innerHTML = '';
            filters.forEach(filter => {
                const swatch = document.createElement('div');
                swatch.className = 'filter-swatch';
                swatch.dataset.filterId = filter.id;
                swatch.innerHTML = `<span>${filter.filter_name}</span>`;
                presetFilterList.appendChild(swatch);
            });
        } catch (error) { console.error('Failed to load filters:', error); }
    };
    
    const startProcessing = async (filterId) => {
        if (!currentMediaFile) { alert('Please select a media file first.'); return; }
        updateUIState('processing');
        try {
            const mediaFormData = new FormData();
            mediaFormData.append('file', currentMediaFile);
            const uploadResponse = await apiRequest('/api/media/upload', { method: 'POST', body: mediaFormData });
            
            const processResponse = await apiRequest('/api/process', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ media_id: uploadResponse.id, filter_id: filterId }),
            });
            
            const blob = await apiRequest(`/api/media/download/${processResponse.processed_media_id}`, { responseType: 'blob' });
            downloadLink.href = URL.createObjectURL(blob);
            downloadLink.download = processResponse.processed_filename;
            updateUIState('complete');
        } catch (error) {
            alert(`Processing failed: ${error.message}`);
            updateUIState('file_selected');
        }
    };
    
    const fetchAndShowUserMedia = async () => {
        try {
            const mediaItems = await apiRequest('/api/media/');
            userMediaList.innerHTML = '';
            if (mediaItems.length === 0) {
                userMediaList.innerHTML = '<li>Your media library is empty.</li>';
                return;
            }
            mediaItems.forEach(item => {
                const li = document.createElement('li');
                li.className = 'media-list-item';
                li.innerHTML = `
                    <div class="media-item-info">
                        <i class="fas ${item.media_type.startsWith('video') ? 'fa-file-video' : 'fa-file-image'}"></i>
                        <span>${item.original_filename}</span>
                    </div>
                    <a href="#" class="btn btn-primary" data-media-id="${item.id}" data-filename="${item.original_filename}">Download</a>
                `;
                userMediaList.appendChild(li);
            });
            modal.classList.remove('hidden');
        } catch (error) { alert(`Failed to load library: ${error.message}`); }
    };
    
    // --- EVENT LISTENERS ---
    loginForm.addEventListener('submit', handleLogin);
    logoutButton.addEventListener('click', handleLogout);
    
    mediaDropZone.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', (e) => handleFileSelect(e.target.files[0]));
    cancelSelectionButton.addEventListener('click', (e) => {
        e.stopPropagation();
        updateUIState('initial');
    });

    filterBar.addEventListener('click', (e) => {
        const swatch = e.target.closest('.filter-swatch');
        if (!swatch || !filterBar.classList.contains('active')) return;

        if (swatch.id === 'upload-filter-box') {
            lutInput.click();
            return;
        }

        document.querySelectorAll('.filter-swatch.selected').forEach(s => s.classList.remove('selected'));
        swatch.classList.add('selected');
        startProcessing(swatch.dataset.filterId);
    });

    mediaLibraryButton.addEventListener('click', fetchAndShowUserMedia);
    modalCloseButton.addEventListener('click', () => modal.classList.add('hidden'));
    modal.addEventListener('click', (e) => {
        if (e.target === modal) modal.classList.add('hidden');
    });

    // --- INITIALIZATION ---
    jwtToken = localStorage.getItem('jwt_token');
    if (jwtToken) {
        initializeApp();
    } else {
        loginView.classList.remove('hidden');
        appView.classList.add('hidden');
    }
});