import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './QuoteCalculator.css';

// Use relative URLs for production, or localhost:8000 for local dev
const API_BASE_URL = process.env.NODE_ENV === 'production' ? '' : 'http://localhost:8000';

function QuoteCalculator({ sessionToken }) {
  const [requirements, setRequirements] = useState('');
  const [quoteHistory, setQuoteHistory] = useState([]);
  const [uploadedQuotes, setUploadedQuotes] = useState([]);
  const [generatedQuote, setGeneratedQuote] = useState(null);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState({ text: '', type: '' });
  const fileInputRef = React.useRef(null);

  useEffect(() => {
    loadUploadedQuotes();
    loadQuoteHistory();
  }, []);

  const loadUploadedQuotes = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/quotes/uploaded`, {
        headers: sessionToken ? { 'Authorization': sessionToken } : {}
      });
      setUploadedQuotes(response.data.quotes || []);
    } catch (error) {
      console.error('Error loading uploaded quotes:', error);
    }
  };

  const loadQuoteHistory = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/quotes/history`, {
        headers: sessionToken ? { 'Authorization': sessionToken } : {}
      });
      setQuoteHistory(response.data.quotes || []);
    } catch (error) {
      console.error('Error loading quote history:', error);
    }
  };

  const showMessage = (text, type) => {
    setMessage({ text, type });
    setTimeout(() => setMessage({ text: '', type: '' }), 5000);
  };

  const handleQuoteUpload = async (event) => {
    const files = event.target.files;
    if (!files || files.length === 0) return;

    // Filter for valid quote files
    const validFiles = Array.from(files).filter(file => 
      file.name.endsWith('.xlsx') || file.name.endsWith('.xls') || file.name.endsWith('.csv')
    );

    if (validFiles.length === 0) {
      showMessage('엑셀(.xlsx, .xls) 또는 CSV 파일만 업로드 가능합니다', 'error');
      return;
    }

    if (validFiles.length < files.length) {
      showMessage(`${files.length - validFiles.length}개 파일이 건너뛰어졌습니다 (지원하지 않는 형식)`, 'error');
    }

    setUploading(true);
    let successCount = 0;
    let failCount = 0;

    // Upload files sequentially
    for (let i = 0; i < validFiles.length; i++) {
      const file = validFiles[i];
      const formData = new FormData();
      formData.append('file', file);

      try {
        await axios.post(`${API_BASE_URL}/api/quotes/upload`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });

        successCount++;
        showMessage(`${file.name}: 업로드 및 학습 완료`, 'success');
      } catch (error) {
        console.error(`Error uploading quote ${file.name}:`, error);
        failCount++;
        showMessage(`${file.name}: 업로드 실패 - ${error.response?.data?.detail || error.message}`, 'error');
      }

      // Small delay between uploads
      if (i < validFiles.length - 1) {
        await new Promise(resolve => setTimeout(resolve, 500));
      }
    }

    setUploading(false);
    event.target.value = '';

    if (successCount > 0) {
      showMessage(`✅ ${successCount}개 견적서가 성공적으로 업로드되었습니다`, 'success');
      loadUploadedQuotes();
    }

    if (failCount > 0) {
      showMessage(`❌ ${failCount}개 견적서 업로드 실패`, 'error');
    }
  };

  const handleGenerateQuote = async () => {
    if (!requirements.trim()) {
      showMessage('요구사항을 입력해주세요', 'error');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE_URL}/api/quotes/generate`, {
        requirements: requirements,
      }, {
        headers: sessionToken ? { 'Authorization': sessionToken } : {}
      });

      setGeneratedQuote(response.data.quote);
      showMessage('견적이 생성되었습니다', 'success');
      loadQuoteHistory();
    } catch (error) {
      console.error('Error generating quote:', error);
      showMessage('견적 생성 실패', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadExcel = async () => {
    if (!generatedQuote) return;

    try {
      const response = await axios.post(
        `${API_BASE_URL}/api/quotes/${generatedQuote.id}/export`,
        { format: 'excel' },
        { 
          responseType: 'blob',
          headers: sessionToken ? { 'Authorization': sessionToken } : {}
        }
      );

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `견적서_${generatedQuote.id}.xlsx`);
      document.body.appendChild(link);
      link.click();
      link.remove();

      showMessage('엑셀 파일이 다운로드되었습니다', 'success');
    } catch (error) {
      console.error('Error downloading Excel:', error);
      showMessage('다운로드 실패', 'error');
    }
  };

  const handleDownloadCSV = async () => {
    if (!generatedQuote) return;

    try {
      const response = await axios.post(
        `${API_BASE_URL}/api/quotes/${generatedQuote.id}/export`,
        { format: 'csv' },
        { 
          responseType: 'blob',
          headers: sessionToken ? { 'Authorization': sessionToken } : {}
        }
      );

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `견적서_${generatedQuote.id}.csv`);
      document.body.appendChild(link);
      link.click();
      link.remove();

      showMessage('CSV 파일이 다운로드되었습니다', 'success');
    } catch (error) {
      console.error('Error downloading CSV:', error);
      showMessage('다운로드 실패', 'error');
    }
  };

  return (
    <div className="quote-calculator">
      <div className="quote-header">
        <h2>💰 견적 계산기</h2>
        <p className="subtitle">과거 견적서를 학습하여 새로운 견적을 자동 생성합니다</p>
      </div>

      {message.text && (
        <div className={`quote-message ${message.type}`}>
          {message.text}
        </div>
      )}

      <div className="quote-container">
        {/* 왼쪽: 견적서 업로드 및 학습 */}
        <div className="quote-left-panel">
          <div className="quote-section">
            <h3>📤 견적서 업로드</h3>
            <p className="section-description">
              과거 견적서(엑셀, CSV)를 업로드하여 시스템이 학습하도록 합니다
            </p>
            <input
              ref={fileInputRef}
              type="file"
              accept=".xlsx,.xls,.csv"
              onChange={handleQuoteUpload}
              disabled={uploading}
              multiple
              style={{ display: 'none' }}
            />
            <button
              className="upload-button"
              onClick={() => fileInputRef.current?.click()}
              disabled={uploading}
            >
              {uploading ? '업로드 중...' : '📁 견적서 선택 (여러 개 가능)'}
            </button>

            {uploadedQuotes.length > 0 && (
              <div className="uploaded-quotes">
                <h4>업로드된 견적서 ({uploadedQuotes.length})</h4>
                <ul>
                  {uploadedQuotes.map((quote) => (
                    <li key={quote.id}>
                      <span className="quote-name">{quote.filename}</span>
                      <span className="quote-date">
                        {new Date(quote.uploaded_at).toLocaleDateString('ko-KR')}
                      </span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>

        {/* 오른쪽: 요구사항 입력 및 견적 생성 */}
        <div className="quote-right-panel">
          <div className="quote-section">
            <h3>✍️ 요구사항 입력</h3>
            <p className="section-description">
              새로운 프로젝트의 요구사항을 입력하세요
            </p>
            <textarea
              className="requirements-input"
              value={requirements}
              onChange={(e) => setRequirements(e.target.value)}
              placeholder="예: 100명 규모의 세미나, 3일간 진행, 강의실 2개, 식사 제공, 호텔 숙박..."
              rows={8}
            />
            <button
              className="generate-button"
              onClick={handleGenerateQuote}
              disabled={loading || !requirements.trim()}
            >
              {loading ? '생성 중...' : '🎯 견적 생성'}
            </button>
          </div>

          {generatedQuote && (
            <div className="quote-section quote-result">
              <h3>📊 생성된 견적</h3>
              <div className="quote-summary">
                <div className="quote-total">
                  <span className="total-label">총 예산</span>
                  <span className="total-amount">
                    {generatedQuote.total_amount?.toLocaleString('ko-KR')}원
                  </span>
                </div>
              </div>

              <div className="quote-items">
                <h4>항목별 상세</h4>
                <table className="quote-table">
                  <thead>
                    <tr>
                      <th>항목</th>
                      <th>단가</th>
                      <th>수량</th>
                      <th>금액</th>
                    </tr>
                  </thead>
                  <tbody>
                    {generatedQuote.items?.map((item, index) => (
                      <tr key={index}>
                        <td>{item.name}</td>
                        <td>{item.unit_price?.toLocaleString('ko-KR')}원</td>
                        <td>{item.quantity}</td>
                        <td>{item.amount?.toLocaleString('ko-KR')}원</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <div className="quote-actions">
                <button className="download-button excel" onClick={handleDownloadExcel}>
                  📊 엑셀 다운로드
                </button>
                <button className="download-button csv" onClick={handleDownloadCSV}>
                  📄 CSV 다운로드
                </button>
              </div>
            </div>
          )}

          {quoteHistory.length > 0 && (
            <div className="quote-section">
              <h3>📜 견적 이력</h3>
              <div className="quote-history">
                {quoteHistory.slice(0, 5).map((quote) => (
                  <div key={quote.id} className="history-item">
                    <span className="history-date">
                      {new Date(quote.created_at).toLocaleDateString('ko-KR')}
                    </span>
                    <span className="history-amount">
                      {quote.total_amount?.toLocaleString('ko-KR')}원
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default QuoteCalculator;

