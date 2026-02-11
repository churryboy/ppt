import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import Login from './Login';
import QuoteCalculator from './QuoteCalculator';
import './App.css';

// Use relative URLs for API calls (works both locally with proxy and in production)
const API_BASE_URL = '';

function App() {
  const [presentations, setPresentations] = useState([]);
  const [selectedPresentation, setSelectedPresentation] = useState(null);
  const [sessionToken, setSessionToken] = useState(localStorage.getItem('sessionToken'));
  const [currentUser, setCurrentUser] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [allSlides, setAllSlides] = useState([]);
  const [archivedSlides, setArchivedSlides] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState({ fileName: '', percent: 0, processing: false });
  const [activeTab, setActiveTab] = useState('presentations'); // presentations, files, archives
  const [activeMainMenu, setActiveMainMenu] = useState(null); // null, 'quote', 'attendee', 'moderator', 'analyzer', 'search'
  const [message, setMessage] = useState({ text: '', type: '' });
  const [sortBy, setSortBy] = useState('recent'); // recent, oldest, downloads
  const [expandedMenus, setExpandedMenus] = useState({ '시각화 검색기': true }); // Track expanded menu items
  const fileInputRef = useRef(null);

  // Configure axios to include auth token
  useEffect(() => {
    if (sessionToken) {
      axios.defaults.headers.common['Authorization'] = sessionToken;
    } else {
      delete axios.defaults.headers.common['Authorization'];
    }
  }, [sessionToken]);

  const handleLogin = (token, user) => {
    setSessionToken(token);
    setCurrentUser(user);
    localStorage.setItem('sessionToken', token);
    showMessage(`Welcome, ${user.username}!`, 'success');
  };

  const handleLogout = async () => {
    try {
      await axios.post(`${API_BASE_URL}/api/auth/logout`);
    } catch (error) {
      console.error('Logout error:', error);
    }
    
    setSessionToken(null);
    setCurrentUser(null);
    localStorage.removeItem('sessionToken');
    setPresentations([]);
    setAllSlides([]);
    setArchivedSlides([]);
    setSearchResults([]);
    showMessage('Logged out successfully', 'info');
  };

  // Verify session on mount
  useEffect(() => {
    const verifySession = async () => {
      if (sessionToken) {
        try {
          const response = await axios.get(`${API_BASE_URL}/api/auth/me`);
          setCurrentUser(response.data.user);
        } catch (error) {
          console.error('Session verification failed:', error);
          handleLogout();
        }
      }
    };
    
    verifySession();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (sessionToken && currentUser) {
      loadPresentations();
      loadAllSlides();
      loadArchivedSlides();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sessionToken, currentUser]);

  const loadAllSlides = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/presentations`);
      const presentations = response.data.presentations;
      
      // Fetch all slides from all presentations
      const allSlidesPromises = presentations.map(pres =>
        axios.get(`${API_BASE_URL}/api/presentations/${pres.id}`)
      );
      
      const slidesResponses = await Promise.all(allSlidesPromises);
      const slides = slidesResponses.flatMap(res => 
        res.data.slides.map(slide => ({
          ...slide,
          presentation: res.data.presentation
        }))
      );
      
      setAllSlides(slides);
    } catch (error) {
      console.error('Error loading slides:', error);
    }
  };

  const loadArchivedSlides = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/archives`);
      setArchivedSlides(response.data.archived_slides);
    } catch (error) {
      console.error('Error loading archived slides:', error);
    }
  };

  const handleArchiveSlide = async (slideId, slideTitle) => {
    try {
      await axios.post(`${API_BASE_URL}/api/slides/${slideId}/archive`);
      showMessage(`📌 "${slideTitle}" archived successfully`, 'success');
      loadArchivedSlides();
    } catch (error) {
      console.error('Error archiving slide:', error);
      showMessage('Failed to archive slide', 'error');
    }
  };

  const handleDeleteArchivedSlide = async (archiveId, slideTitle) => {
    if (!window.confirm(`Delete archived slide "${slideTitle}"?`)) return;
    
    try {
      await axios.delete(`${API_BASE_URL}/api/archives/${archiveId}`);
      showMessage('Archived slide deleted', 'success');
      loadArchivedSlides();
    } catch (error) {
      console.error('Error deleting archived slide:', error);
      showMessage('Failed to delete archived slide', 'error');
    }
  };

  const showMessage = (text, type = 'info') => {
    setMessage({ text, type });
    setTimeout(() => setMessage({ text: '', type: '' }), 5000);
  };

  const loadPresentations = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/presentations`);
      setPresentations(response.data.presentations);
    } catch (error) {
      console.error('Error loading presentations:', error);
      showMessage('Failed to load presentations', 'error');
    }
  };

  const handleFileUpload = async (event) => {
    const files = event.target.files;
    if (!files || files.length === 0) return;

    await uploadFiles(Array.from(files));
    event.target.value = '';
  };

  const uploadFiles = async (files) => {
    // Filter for valid PowerPoint files
    const validFiles = files.filter(file => 
      file.name.endsWith('.pptx') || file.name.endsWith('.ppt')
    );

    if (validFiles.length === 0) {
      showMessage('Please upload PowerPoint files (.pptx or .ppt)', 'error');
      return;
    }

    if (validFiles.length < files.length) {
      showMessage(`${files.length - validFiles.length} file(s) skipped (not PowerPoint)`, 'error');
    }

    setUploading(true);
    let successCount = 0;
    let failCount = 0;

    for (let i = 0; i < validFiles.length; i++) {
      const file = validFiles[i];
      const formData = new FormData();
      formData.append('file', file);

      try {
        setUploadProgress({ 
          fileName: file.name, 
          percent: 0,
          processing: false,
          current: i + 1,
          total: validFiles.length
        });

        const response = await axios.post(`${API_BASE_URL}/api/upload`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
          onUploadProgress: (progressEvent) => {
            // Upload progress is 0-50%, processing will be 50-100%
            const uploadPercent = Math.round((progressEvent.loaded * 50) / progressEvent.total);
            setUploadProgress({ 
              fileName: file.name, 
              percent: uploadPercent,
              processing: false,
              current: i + 1,
              total: validFiles.length
            });
          },
        }).then((res) => {
          // File uploaded, now processing
          setUploadProgress({ 
            fileName: file.name, 
            percent: 50,
            processing: true,
            current: i + 1,
            total: validFiles.length
          });
          return res;
        });
        
        // Processing complete, show 100%
        setUploadProgress({ 
          fileName: file.name, 
          percent: 100,
          processing: false,
          current: i + 1,
          total: validFiles.length
        });
        
        successCount++;
        showMessage(`${file.name}: ${response.data.slide_count} slides parsed`, 'success');
      } catch (error) {
        console.error('Error uploading file:', error);
        failCount++;
        showMessage(`${file.name}: ${error.response?.data?.detail || 'Failed to upload'}`, 'error');
      }

      // Small delay between uploads to avoid overwhelming the server
      if (i < validFiles.length - 1) {
        await new Promise(resolve => setTimeout(resolve, 500));
      }
    }

    setUploading(false);
    setUploadProgress({ fileName: '', percent: 0, processing: false });
    
      if (successCount > 0) {
        showMessage(`✅ Successfully uploaded ${successCount} presentation(s)`, 'success');
        loadPresentations();
        loadAllSlides();
      }
    
    if (failCount > 0) {
      showMessage(`❌ Failed to upload ${failCount} presentation(s)`, 'error');
    }
  };


  const handlePresentationClick = async (presentationId) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/presentations/${presentationId}`);
      setSelectedPresentation(response.data);
      setActiveTab('view');
    } catch (error) {
      console.error('Error loading presentation:', error);
      showMessage('Failed to load presentation details', 'error');
    }
  };

  const handleSearch = async (query) => {
    if (!query.trim()) {
      setSearchResults([]);
      return;
    }

    try {
      const response = await axios.get(`${API_BASE_URL}/api/search`, {
        params: { q: query }
      });
      setSearchResults(response.data.results);
    } catch (error) {
      console.error('Error searching:', error);
      showMessage('Search failed', 'error');
    }
  };

  const handleSearchChange = (e) => {
    const query = e.target.value;
    setSearchQuery(query);
    handleSearch(query);
  };

  const handleImageDownload = async (imageUrl, slideTitle, slideNumber, slideId) => {
    try {
      const response = await fetch(imageUrl);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${slideTitle.replace(/[^a-z0-9]/gi, '_')}_slide_${slideNumber}.png`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      // Track download
      try {
        await axios.post(`${API_BASE_URL}/api/slides/${slideId}/download`);
        // Refresh slides to get updated download count
        loadAllSlides();
      } catch (error) {
        console.error('Error tracking download:', error);
      }
    } catch (error) {
      console.error('Error downloading image:', error);
      showMessage('Failed to download image', 'error');
    }
  };

  const getSortedSlides = (slides) => {
    const slidesCopy = [...slides];
    switch (sortBy) {
      case 'recent':
        return slidesCopy.sort((a, b) => {
          const dateA = a.presentation?.created_at || a.created_at || '';
          const dateB = b.presentation?.created_at || b.created_at || '';
          return new Date(dateB) - new Date(dateA);
        });
      case 'oldest':
        return slidesCopy.sort((a, b) => {
          const dateA = a.presentation?.created_at || a.created_at || '';
          const dateB = b.presentation?.created_at || b.created_at || '';
          return new Date(dateA) - new Date(dateB);
        });
      case 'downloads':
        return slidesCopy.sort((a, b) => (b.download_count || 0) - (a.download_count || 0));
      default:
        return slidesCopy;
    }
  };

  const handleDelete = async (presentationId) => {
    if (!window.confirm('Are you sure you want to delete this presentation?')) {
      return;
    }

    try {
      await axios.delete(`${API_BASE_URL}/api/presentations/${presentationId}`);
      showMessage('Presentation deleted successfully', 'success');
      loadPresentations();
      if (selectedPresentation?.presentation.id === presentationId) {
        setSelectedPresentation(null);
        setActiveTab('presentations');
      }
    } catch (error) {
      console.error('Error deleting presentation:', error);
      showMessage('Failed to delete presentation', 'error');
    }
  };

  // Show login if not authenticated
  if (!sessionToken || !currentUser) {
    return <Login onLogin={handleLogin} />;
  }

  return (
    <div className="App">
      {/* Top Navigation Bar */}
      <nav className="top-nav">
        <div className="nav-left">
          <h1 className="logo">📊 보고서 저장소</h1>
          <span className="user-info">Logged in as: {currentUser.username}</span>
        </div>
        <div className="nav-right">
          {uploading && (
            <div className="upload-progress-container">
              <div className="upload-progress-info">
                <span className="upload-file-name">
                  {uploadProgress.total > 1 && `(${uploadProgress.current}/${uploadProgress.total}) `}
                  {uploadProgress.fileName}
                  {uploadProgress.processing && ' - Processing...'}
                </span>
                <span className="upload-percentage">{uploadProgress.percent}%</span>
              </div>
              <div className="progress-bar">
                <div 
                  className={`progress-bar-fill ${uploadProgress.processing ? 'processing' : ''}`}
                  style={{ width: `${uploadProgress.percent}%` }}
                ></div>
              </div>
              {uploadProgress.processing && (
                <div className="processing-status">Generating slide screenshots...</div>
              )}
            </div>
          )}
          <button className="profile-button" onClick={handleLogout} title="Logout">
            <span className="profile-icon">👤</span>
          </button>
        </div>
      </nav>

      <div className="app-body">
        {/* Left Sidebar */}
        <aside className="sidebar">
          <nav className="sidebar-nav">
            {/* 견적 계산기 */}
            <div className="menu-item">
              <button 
                className={`menu-header ${activeMainMenu === 'quote' ? 'active' : ''}`}
                onClick={() => {
                  setActiveMainMenu(activeMainMenu === 'quote' ? null : 'quote');
                  setActiveTab(null);
                }}
              >
                <span className="nav-icon">💰</span>
                <span className="nav-label">견적 계산기</span>
              </button>
            </div>

            {/* 참석자 선별기 */}
            <div className="menu-item">
              <button className="menu-header">
                <span className="nav-icon">👥</span>
                <span className="nav-label">참석자 선별기</span>
              </button>
            </div>

            {/* AI 모더레이터 */}
            <div className="menu-item">
              <button className="menu-header">
                <span className="nav-icon">🤖</span>
                <span className="nav-label">AI 모더레이터</span>
              </button>
            </div>

            {/* 결과 분석기 */}
            <div className="menu-item">
              <button className="menu-header">
                <span className="nav-icon">📊</span>
                <span className="nav-label">결과 분석기</span>
              </button>
            </div>

            {/* 시각화 검색기 - Expandable */}
            <div className="menu-item">
              <button 
                className="menu-header"
                onClick={() => setExpandedMenus(prev => ({ ...prev, '시각화 검색기': !prev['시각화 검색기'] }))}
              >
                <span className="nav-icon">🔍</span>
                <span className="nav-label">시각화 검색기</span>
                <span className="expand-icon">{expandedMenus['시각화 검색기'] ? '▼' : '▶'}</span>
              </button>
              {expandedMenus['시각화 검색기'] && (
                <div className="submenu">
                  <button 
                    className="submenu-button"
                    onClick={() => fileInputRef.current?.click()}
                    disabled={uploading}
                  >
                    <span className="nav-icon">📤</span>
                    <span className="nav-label">Upload</span>
                  </button>
                  
                  <button 
                    className={`submenu-button ${activeTab === 'presentations' ? 'active' : ''}`}
                    onClick={() => setActiveTab('presentations')}
                  >
                    <span className="nav-icon">🎞️</span>
                    <span className="nav-label">All Slides</span>
                  </button>

                  <button 
                    className={`submenu-button ${activeTab === 'files' ? 'active' : ''}`}
                    onClick={() => setActiveTab('files')}
                  >
                    <span className="nav-icon">📁</span>
                    <span className="nav-label">Files</span>
                    <span className="nav-count">{presentations.length}</span>
                  </button>

                  <button 
                    className={`submenu-button ${activeTab === 'archives' ? 'active' : ''}`}
                    onClick={() => setActiveTab('archives')}
                  >
                    <span className="nav-icon">📌</span>
                    <span className="nav-label">Archives</span>
                    <span className="nav-count">{archivedSlides.length}</span>
                  </button>
                </div>
              )}
            </div>
          </nav>
        </aside>

        {/* Hidden file input */}
        <input
          ref={fileInputRef}
          type="file"
          accept=".pptx,.ppt"
          onChange={handleFileUpload}
          disabled={uploading}
          multiple
          style={{ display: 'none' }}
        />

        <main className="main-content">
        <div className="content">
          {/* 견적 계산기 뷰 */}
          {activeMainMenu === 'quote' && (
            <QuoteCalculator sessionToken={sessionToken} />
          )}

          {/* 기존 뷰들 (시각화 검색기 하위) */}
          {activeMainMenu !== 'quote' && (
            <>
          {/* Search Bar and Filters */}
          <div className="search-bar-container">
            <input
              type="text"
              placeholder="🔍 Search presentations by filename, title, content, or notes..."
              value={searchQuery}
              onChange={handleSearchChange}
              className="main-search-input"
            />
            <div className="filter-bar">
              <label className="filter-label">Sort by:</label>
              <div className="filter-buttons">
                <button
                  className={`filter-btn ${sortBy === 'recent' ? 'active' : ''}`}
                  onClick={() => setSortBy('recent')}
                >
                  📅 Newest First
                </button>
                <button
                  className={`filter-btn ${sortBy === 'oldest' ? 'active' : ''}`}
                  onClick={() => setSortBy('oldest')}
                >
                  📅 Oldest First
                </button>
                <button
                  className={`filter-btn ${sortBy === 'downloads' ? 'active' : ''}`}
                  onClick={() => setSortBy('downloads')}
                >
                  ⬇️ Most Downloads
                </button>
              </div>
            </div>
          </div>
        {/* Main View - Show all slides or search results */}
        {activeTab === 'presentations' && (
          <div className="main-view">
            {searchQuery && searchResults.length > 0 ? (
              <>
                <h2 className="section-title">Search Results ({searchResults.length})</h2>
                <div className="slides-container">
                  {getSortedSlides(searchResults.map(r => ({ ...r.slide, presentation: r.presentation }))).map((slide) => (
                    <div key={slide.id} className="slide-card">
                      {slide.image_path && (
                        <div className="slide-image">
                          <img 
                            src={`${API_BASE_URL}/slides/${slide.presentation_id}/${slide.image_path}`}
                            alt={`Slide ${slide.slide_number}`}
                            onError={(e) => e.target.style.display = 'none'}
                          />
                        </div>
                      )}
                      <div className="slide-info">
                        <div className="slide-text-info">
                          <h3>{slide.title}</h3>
                          <p className="slide-presentation-name">{slide.presentation?.filename || slide.presentation?.original_filename}</p>
                        </div>
                        <button
                          className="download-btn-small"
                          onClick={() => handleImageDownload(
                            `${API_BASE_URL}/slides/${slide.presentation_id}/${slide.image_path}`,
                            slide.title,
                            slide.slide_number,
                            slide.id
                          )}
                          title="Download slide"
                        >
                          ⬇️
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </>
            ) : searchQuery ? (
              <div className="empty-state">
                <p>No results found for "{searchQuery}"</p>
              </div>
            ) : (
              <>
                <h2 className="section-title">All Slides ({allSlides.length})</h2>
                <div className="slides-container">
                  {getSortedSlides(allSlides).map((slide) => (
                    <div key={slide.id} className="slide-card">
                      {slide.image_path && (
                        <div className="slide-image">
                          <img 
                            src={`${API_BASE_URL}/slides/${slide.presentation_id}/${slide.image_path}`}
                            alt={`Slide ${slide.slide_number}`}
                            onError={(e) => e.target.style.display = 'none'}
                          />
                        </div>
                      )}
                      <div className="slide-info">
                        <div className="slide-text-info">
                          <h3>{slide.title}</h3>
                          <p className="slide-presentation-name">{slide.presentation.original_filename}</p>
                        </div>
                        <div className="slide-actions">
                          <button
                            className="archive-btn-small"
                            onClick={() => handleArchiveSlide(slide.id, slide.title)}
                            title="Archive slide"
                          >
                            📌
                          </button>
                          <button
                            className="download-btn-small"
                            onClick={() => handleImageDownload(
                              `${API_BASE_URL}/slides/${slide.presentation_id}/${slide.image_path}`,
                              slide.title,
                              slide.slide_number,
                              slide.id
                            )}
                            title="Download slide"
                          >
                            ⬇️
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </>
            )}
          </div>
        )}

        {/* Archives View */}
        {activeTab === 'archives' && (
          <div className="main-view">
            <h2 className="section-title">Archived Slides ({archivedSlides.length})</h2>
            {archivedSlides.length === 0 ? (
              <div className="empty-state">
                <p>No archived slides yet</p>
                <p className="empty-hint">Archive slides to save them independently from their presentations</p>
              </div>
            ) : (
              <div className="slides-container">
                {archivedSlides.map((slide) => (
                  <div key={slide.id} className="slide-card">
                    {slide.image_path && (
                      <div className="slide-image">
                        <img 
                          src={`${API_BASE_URL}/archives/${slide.image_path}`}
                          alt={`Archived slide ${slide.slide_number}`}
                          onError={(e) => e.target.style.display = 'none'}
                        />
                      </div>
                    )}
                    <div className="slide-info">
                      <div className="slide-text-info">
                        <h3>{slide.title}</h3>
                        <p className="slide-presentation-name">{slide.original_presentation_name}</p>
                        <p className="slide-archived-date">Archived: {new Date(slide.archived_at).toLocaleDateString()}</p>
                      </div>
                      <button
                        className="delete-archive-btn-small"
                        onClick={() => handleDeleteArchivedSlide(slide.id, slide.title)}
                        title="Delete from archives"
                      >
                        🗑️
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Files Management View */}
        {activeTab === 'files' && (
          <div className="files-section">
            <h2 className="section-title">Uploaded Files ({presentations.length})</h2>
            {presentations.length === 0 ? (
              <div className="empty-state">
                <p>No files uploaded yet</p>
                <p className="empty-hint">Click the Upload button to add PowerPoint files</p>
              </div>
            ) : (
              <div className="files-list">
                {presentations.map((pres) => (
                  <div key={pres.id} className="file-item">
                    <div className="file-icon">📄</div>
                    <div className="file-info">
                      <h3 className="file-name">{pres.original_filename}</h3>
                      <div className="file-meta">
                        <span className="file-slides">{pres.slide_count} slides</span>
                        <span className="file-divider">•</span>
                        <span className="file-date">
                          {new Date(pres.upload_date).toLocaleDateString()}
                        </span>
                      </div>
                    </div>
                    <div className="file-actions">
                      <button
                        className="view-slides-btn"
                        onClick={() => {
                          setActiveTab('presentations');
                        }}
                        title="View all slides"
                      >
                        👁️ View Slides
                      </button>
                      <button
                        className="delete-file-btn"
                        onClick={() => handleDelete(pres.id, pres.original_filename)}
                        title="Delete file and all slides"
                      >
                        🗑️ Delete
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
            </>
          )}

        </div>
      </main>
      </div>

      {/* Global Message Toast */}
      {message.text && (
        <div className={`message ${message.type}`}>
          {message.text}
        </div>
      )}
    </div>
  );
}

export default App;

