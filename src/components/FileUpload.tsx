import { useState, useRef } from 'react';
import { Upload, FileText, Code, FileCode, Tag, CheckCircle2, Loader2, XCircle, Download, Eye, Bot, Sparkles } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import axios from 'axios';
import '../styles/FileUpload.css';
import '../styles/clean.css';

const API_BASE_URL = 'http://localhost:8000';

interface ProcessStep {
  status: 'pending' | 'processing' | 'completed' | 'error';
  message: string;
  [key: string]: any;
}

interface ProcessResponse {
  success: boolean;
  steps: {
    upload: ProcessStep;
    extract_html: ProcessStep;
    convert_markdown: ProcessStep;
    extract_ticker: ProcessStep;
    save: ProcessStep;
  };
  ticker?: string;
  html_size: number;
  markdown_size: number;
  markdown_preview: string;
  file_path?: string;
  html_file_path?: string;
  indexed?: boolean;
  ready_for_qa?: boolean;
  error?: string;
}

export default function FileUpload() {
  const [file, setFile] = useState<File | null>(null);
  const [processing, setProcessing] = useState(false);
  const [result, setResult] = useState<ProcessResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showPreview, setShowPreview] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setResult(null);
      setError(null);
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setProcessing(true);
    setError(null);
    setResult(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post<ProcessResponse>(
        `${API_BASE_URL}/upload`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );

      setResult(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Upload failed');
      console.error('Upload error:', err);
    } finally {
      setProcessing(false);
    }
  };

  const formatBytes = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  const getStepIcon = (status: ProcessStep['status']) => {
    switch (status) {
      case 'completed':
        return <CheckCircle2 size={20} className="step-icon completed" />;
      case 'processing':
        return <Loader2 size={20} className="step-icon processing" />;
      case 'error':
        return <XCircle size={20} className="step-icon error" />;
      default:
        return <div className="step-icon pending" />;
    }
  };

  const steps = [
    {
      key: 'upload',
      label: 'Uploading',
      icon: Upload,
      description: 'Uploading TXT file to server',
    },
    {
      key: 'extract_html',
      label: 'Extract HTML',
      icon: Code,
      description: 'Extracting HTML from full-submission.txt',
    },
    {
      key: 'convert_markdown',
      label: 'Convert to Markdown',
      icon: FileCode,
      description: 'Converting HTML to Markdown format',
    },
    {
      key: 'extract_ticker',
      label: 'Extract Ticker',
      icon: Tag,
      description: 'Identifying company ticker symbol',
    },
    {
      key: 'save',
      label: 'Save File',
      icon: FileText,
      description: 'Saving processed Markdown file',
    },
  ];

  return (
    <div className="file-upload-container">
      <div className="file-upload-card">
        <h2 className="upload-title">Process SEC Filing</h2>
        <p className="upload-subtitle">
          Upload a full-submission.txt file to process through the pipeline
        </p>

        {/* File Input */}
        <div className="file-input-section">
          <input
            ref={fileInputRef}
            type="file"
            accept=".txt"
            onChange={handleFileSelect}
            className="file-input"
            disabled={processing}
          />
          <button
            onClick={() => fileInputRef.current?.click()}
            className="file-select-button"
            disabled={processing}
          >
            <Upload size={18} />
            {file ? file.name : 'Select TXT File'}
          </button>
          {file && (
            <div className="file-info">
              <span>{formatBytes(file.size)}</span>
              <button
                onClick={() => {
                  setFile(null);
                  setResult(null);
                  setError(null);
                }}
                className="file-remove"
              >
                <XCircle size={16} />
              </button>
            </div>
          )}
        </div>

        {/* Process Button */}
        <button
          onClick={handleUpload}
          disabled={!file || processing}
          className="process-button"
        >
          {processing ? (
            <>
              <Loader2 size={18} className="spinning" />
              Processing...
            </>
          ) : (
            <>
              <FileText size={18} />
              Process File
            </>
          )}
        </button>

        {/* Error Display */}
        {error && (
          <div className="error-message">
            <XCircle size={20} />
            <span>{error}</span>
          </div>
        )}

        {/* Steps Progress */}
        {result && (
          <div className="steps-container">
            <h3 className="steps-title">Processing Steps</h3>
            {steps.map((step, index) => {
              const stepData = result.steps[step.key as keyof typeof result.steps];
              const StepIcon = step.icon;

              return (
                <div
                  key={step.key}
                  className={`step-item ${stepData.status}`}
                >
                  <div className="step-header">
                    <div className="step-icon-wrapper">
                      {getStepIcon(stepData.status)}
                    </div>
                    <div className="step-content">
                      <div className="step-label">
                        <StepIcon size={18} />
                        <span>{step.label}</span>
                      </div>
                      <div className="step-message">{stepData.message}</div>
                      {stepData.size && (
                        <div className="step-meta">
                          Size: {formatBytes(stepData.size)}
                        </div>
                      )}
                      {stepData.ticker && (
                        <div className="step-meta">
                          Ticker: <strong>{stepData.ticker}</strong>
                        </div>
                      )}
                      {stepData.lines && (
                        <div className="step-meta">
                          Lines: {stepData.lines.toLocaleString()}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* Results */}
        {result && result.success && (
          <div className="results-section">
            <div className="results-header">
              <h3>Processing Complete!</h3>
              {result.ticker && (
                <div className="ticker-badge">
                  <Tag size={16} />
                  {result.ticker}
                </div>
              )}
            </div>

            <div className="results-stats">
              <div className="stat-item">
                <span className="stat-label">HTML Size</span>
                <span className="stat-value">{formatBytes(result.html_size)}</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Markdown Size</span>
                <span className="stat-value">{formatBytes(result.markdown_size)}</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Compression</span>
                <span className="stat-value">
                  {((1 - result.markdown_size / result.html_size) * 100).toFixed(1)}%
                </span>
              </div>
            </div>

            {/* Ready for QnA Badge */}
            {result.ready_for_qa && (
              <div className="ready-badge">
                <Bot size={18} />
                <div className="ready-content">
                  <div className="ready-title">Ready for QnA & Agentic Analysis!</div>
                  <div className="ready-description">
                    This file has been indexed and is ready to use in the Analyze tab
                  </div>
                </div>
                <Sparkles size={18} className="sparkle-icon" />
              </div>
            )}

            <div className="results-actions">
              <button
                onClick={() => setShowPreview(!showPreview)}
                className="action-button"
              >
                <Eye size={18} />
                {showPreview ? 'Hide' : 'Show'} Preview
              </button>
              {result.file_path && (
                <a
                  href={`${API_BASE_URL}/files/${encodeURIComponent(result.file_path.replace(/\\/g, '/'))}`}
                  download
                  className="action-button"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  <Download size={18} />
                  Download MD
                </a>
              )}
              {result.html_file_path && (
                <a
                  href={`${API_BASE_URL}/files/${encodeURIComponent(result.html_file_path.replace(/\\/g, '/'))}`}
                  download
                  className="action-button"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  <Code size={18} />
                  Download HTML
                </a>
              )}
            </div>

            {showPreview && (
              <div className="preview-container">
                <div className="preview-header">
                  <h4>Markdown Preview</h4>
                  <span className="preview-size">
                    {formatBytes(result.markdown_size)}
                  </span>
                </div>
                <div className="preview-content">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>{result.markdown_preview}</ReactMarkdown>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
