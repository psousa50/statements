import React, { useState, useRef, useCallback } from 'react';
import { Card, Button, Spinner } from 'react-bootstrap';
import styles from './UploadPage.module.css';

interface FileUploadZoneProps {
  onFileSelected: (file: File) => void;
  isLoading: boolean;
}

const FileUploadZone: React.FC<FileUploadZoneProps> = ({ onFileSelected, isLoading }) => {
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback(() => {
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      onFileSelected(e.dataTransfer.files[0]);
    }
  }, [onFileSelected]);

  const handleFileChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      onFileSelected(e.target.files[0]);
    }
  }, [onFileSelected]);

  const handleButtonClick = useCallback(() => {
    fileInputRef.current?.click();
  }, []);

  return (
    <Card
      className={`mb-4 ${isDragging ? 'border-primary' : ''}`}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      <Card.Body className="text-center p-5">
        {isLoading ? (
          <div className="py-5">
            <Spinner animation="border" role="status" variant="primary" />
            <p className="mt-3">Analyzing your file...</p>
          </div>
        ) : (
          <>
            <div className="mb-4">
              <i className="bi bi-cloud-upload" style={{ fontSize: '3rem' }}></i>
            </div>
            <h5>Drag and drop your bank statement file here</h5>
            <p className="text-muted">or</p>
            <Button variant="primary" onClick={handleButtonClick}>
              Browse Files
            </Button>
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileChange}
              accept=".csv,.xls,.xlsx"
              style={{ display: 'none' }}
            />
            <p className="mt-3 text-muted">
              Supported formats: CSV, Excel (.xls, .xlsx) - Max 10MB
            </p>
          </>
        )}
      </Card.Body>
    </Card>
  );
};

export default FileUploadZone;
