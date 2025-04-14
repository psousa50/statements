import React, { useState, useCallback, useRef } from 'react';
import {
  Container, Card, Button, Alert, Spinner,
  Table, Form, Row, Col, Badge
} from 'react-bootstrap';
import { useFileUpload, useSources } from '../hooks/useQueries';
import axios from 'axios';

// Define types for file analysis response
interface ColumnMapping {
  date: string;
  description: string;
  amount: string;
  debit_amount?: string;
  credit_amount?: string;
  currency?: string;
  balance?: string;
}

interface FileAnalysisResponse {
  source: string | null;
  total_transactions: number;
  total_amount: number;
  date_range_start: string | null;
  date_range_end: string | null;
  column_mappings: ColumnMapping;
  start_row: number;
  file_id: string;
  preview_rows: Record<string, any>[];
}

// Component for file upload zone with drag and drop
const FileUploadZone: React.FC<{
  onFileSelected: (file: File) => void;
  isLoading: boolean;
}> = ({ onFileSelected, isLoading }) => {
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
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
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
            <Button
              variant="primary"
              onClick={handleButtonClick}
            >
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

// Component for analysis summary
const AnalysisSummary: React.FC<{
  analysis: FileAnalysisResponse;
}> = ({ analysis }) => {
  return (
    <Card className="mb-4">
      <Card.Header>
        <h5 className="mb-0">Analysis Summary</h5>
      </Card.Header>
      <Card.Body>
        <Row>
          <Col md={3} className="mb-3">
            <Card className="h-100">
              <Card.Body className="text-center">
                <h6 className="text-muted">Source</h6>
                <h4>{analysis.source || 'Unknown'}</h4>
              </Card.Body>
            </Card>
          </Col>
          <Col md={3} className="mb-3">
            <Card className="h-100">
              <Card.Body className="text-center">
                <h6 className="text-muted">Transactions</h6>
                <h4>{analysis.total_transactions}</h4>
              </Card.Body>
            </Card>
          </Col>
          <Col md={3} className="mb-3">
            <Card className="h-100">
              <Card.Body className="text-center">
                <h6 className="text-muted">Total Amount</h6>
                <h4>{analysis.total_amount.toFixed(2)}</h4>
              </Card.Body>
            </Card>
          </Col>
          <Col md={3} className="mb-3">
            <Card className="h-100">
              <Card.Body className="text-center">
                <h6 className="text-muted">Date Range</h6>
                <h4>
                  {analysis.date_range_start && analysis.date_range_end
                    ? `${new Date(analysis.date_range_start).toLocaleDateString()} - ${new Date(analysis.date_range_end).toLocaleDateString()}`
                    : 'N/A'}
                </h4>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      </Card.Body>
    </Card>
  );
};

// Component for column mapping table
const ColumnMappingTable: React.FC<{
  analysis: FileAnalysisResponse;
  columnMappings: Record<string, string>;
  onColumnMappingChange: (columnName: string, mappingType: string) => void;
  startRow: number;
  onStartRowChange: (startRow: number) => void;
}> = ({ analysis, columnMappings, onColumnMappingChange, startRow, onStartRowChange }) => {
  // Get all original column names from the first preview row
  const originalColumns = analysis.preview_rows.length > 0
    ? Object.keys(analysis.preview_rows[0])
    : [];

  // Column mapping options
  const columnOptions = [
    { value: "date", label: "Date" },
    { value: "description", label: "Description" },
    { value: "amount", label: "Amount" },
    { value: "category", label: "Category (optional)" },
    { value: "ignore", label: "Ignore" }
  ];

  return (
    <Card className="mb-4">
      <Card.Header className="d-flex justify-content-between align-items-center">
        <h5 className="mb-0">Column Mapping</h5>
        <Form.Group className="mb-0 d-flex align-items-center">
          <Form.Label className="me-2 mb-0">Data starts at row:</Form.Label>
          <Form.Control
            type="number"
            min="0"
            value={startRow}
            onChange={(e) => onStartRowChange(parseInt(e.target.value))}
            style={{ width: '80px' }}
          />
        </Form.Group>
      </Card.Header>
      <Card.Body className="p-0">
        <div className="table-responsive">
          <Table bordered hover>
            <thead>
              <tr>
                {originalColumns.map((column, index) => (
                  <th key={index} className="text-center">
                    <Form.Select
                      size="sm"
                      value={columnMappings[column] || 'ignore'}
                      onChange={(e) => onColumnMappingChange(column, e.target.value)}
                    >
                      {columnOptions.map(option => (
                        <option key={option.value} value={option.value}>
                          {option.label}
                        </option>
                      ))}
                    </Form.Select>
                    <Badge bg="secondary" className="mt-2 d-block">
                      {column}
                    </Badge>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {analysis.preview_rows.map((row, rowIndex) => (
                <tr key={rowIndex}>
                  {originalColumns.map((column, colIndex) => (
                    <td key={colIndex}>
                      {row[column] !== null ? String(row[column]) : ''}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </Table>
        </div>
      </Card.Body>
    </Card>
  );
};

// Component for validation messages
const ValidationMessages: React.FC<{
  columnMappings: Record<string, string>;
  isValid: boolean;
}> = ({ columnMappings, isValid }) => {
  // Check if required columns are mapped
  const hasDateColumn = Object.values(columnMappings).includes('date');
  const hasDescriptionColumn = Object.values(columnMappings).includes('description');
  const hasAmountColumn = Object.values(columnMappings).includes('amount');

  if (isValid) {
    return (
      <Alert variant="success" className="mb-4">
        <Alert.Heading>Ready to Upload</Alert.Heading>
        <p>Your column mappings look good! Click "Finalize Upload" to import your transactions.</p>
      </Alert>
    );
  }

  return (
    <Alert variant="warning" className="mb-4">
      <Alert.Heading>Please Fix the Following Issues:</Alert.Heading>
      <ul className="mb-0">
        {!hasDateColumn && (
          <li>Date column is required - please select which column contains transaction dates</li>
        )}
        {!hasDescriptionColumn && (
          <li>Description column is required - please select which column contains transaction descriptions</li>
        )}
        {!hasAmountColumn && (
          <li>Amount column is required - please select which column contains transaction amounts</li>
        )}
      </ul>
    </Alert>
  );
};

// Main Upload Page component
const UploadPage: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [sourceId, setSourceId] = useState<number | undefined>(undefined);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<FileAnalysisResponse | null>(null);
  const [columnMappings, setColumnMappings] = useState<Record<string, string>>({});
  const [startRow, setStartRow] = useState(0);
  const [uploadResult, setUploadResult] = useState<{
    success: boolean;
    message: string;
    processed: number;
    skipped: number;
  } | null>(null);

  const { mutate: uploadFile } = useFileUpload();
  const { data: sources, isLoading: isLoadingSources } = useSources();

  // Handle file selection
  const handleFileSelected = useCallback(async (selectedFile: File) => {
    setFile(selectedFile);
    setIsAnalyzing(true);
    setAnalysisResult(null);
    setUploadResult(null);

    // Create form data for file upload
    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      // Call the analyze endpoint
      const response = await axios.post<FileAnalysisResponse>(
        `${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/transactions/analyze`,
        formData
      );

      setAnalysisResult(response.data);

      // Initialize column mappings from the response
      const initialMappings: Record<string, string> = {};
      if (response.data.preview_rows.length > 0) {
        const columns = Object.keys(response.data.preview_rows[0]);

        // Map columns based on the analysis response
        const columnMap = response.data.column_mappings;
        for (const column of columns) {
          if (column === columnMap.date) {
            initialMappings[column] = 'date';
          } else if (column === columnMap.description) {
            initialMappings[column] = 'description';
          } else if (column === columnMap.amount) {
            initialMappings[column] = 'amount';
          } else {
            initialMappings[column] = 'ignore';
          }
        }
      }

      setColumnMappings(initialMappings);
      setStartRow(response.data.start_row);

    } catch (error) {
      console.error('Error analyzing file:', error);
      setUploadResult({
        success: false,
        message: 'Error analyzing file. Please try again.',
        processed: 0,
        skipped: 0,
      });
    } finally {
      setIsAnalyzing(false);
    }
  }, []);

  // Handle column mapping change
  const handleColumnMappingChange = useCallback((columnName: string, mappingType: string) => {
    setColumnMappings(prev => ({
      ...prev,
      [columnName]: mappingType
    }));
  }, []);

  // Handle start row change
  const handleStartRowChange = useCallback((newStartRow: number) => {
    setStartRow(newStartRow);
  }, []);

  // Handle source change
  const handleSourceChange = useCallback((e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value;
    const parsedValue = value ? parseInt(value) : undefined;
    setSourceId(parsedValue);
  }, []);

  // Check if mappings are valid
  const isMappingValid = useCallback(() => {
    const mappingValues = Object.values(columnMappings);
    return (
      mappingValues.includes('date') &&
      mappingValues.includes('description') &&
      mappingValues.includes('amount')
    );
  }, [columnMappings]);

  // Handle final upload
  const handleFinalUpload = useCallback(async () => {
    if (!file || !analysisResult || !isMappingValid()) {
      return;
    }

    setIsUploading(true);

    // Create form data for file upload
    const formData = new FormData();
    formData.append('file', file);
    if (sourceId) {
      formData.append('source_id', sourceId.toString());
    }

    // TODO: In a real implementation, we would also send the column mappings
    // and start row to the backend for processing

    uploadFile(
      { file, sourceId },
      {
        onSuccess: (data) => {
          setUploadResult({
            success: true,
            message: data.message,
            processed: data.transactions_processed,
            skipped: data.skipped_duplicates,
          });
          setFile(null);
          setAnalysisResult(null);
        },
        onError: (error) => {
          setUploadResult({
            success: false,
            message: error instanceof Error ? error.message : 'An error occurred during upload',
            processed: 0,
            skipped: 0,
          });
        },
        onSettled: () => {
          setIsUploading(false);
        }
      }
    );
  }, [file, analysisResult, sourceId, uploadFile, isMappingValid]);

  // Reset the form
  const handleReset = useCallback(() => {
    setFile(null);
    setAnalysisResult(null);
    setColumnMappings({});
    setUploadResult(null);
  }, []);

  return (
    <Container>
      <h1 className="mb-4">Upload Bank Statement</h1>

      {!analysisResult && !uploadResult && (
        <FileUploadZone
          onFileSelected={handleFileSelected}
          isLoading={isAnalyzing}
        />
      )}

      {analysisResult && !uploadResult && (
        <>
          <AnalysisSummary analysis={analysisResult} />

          <Form.Group className="mb-4">
            <Form.Label>Source</Form.Label>
            <Form.Select
              value={sourceId || ''}
              onChange={handleSourceChange}
              disabled={isLoadingSources}
            >
              <option value="">Select a source (optional)</option>
              {sources?.map((source) => (
                <option key={source.id} value={source.id}>
                  {source.name}
                </option>
              ))}
            </Form.Select>
            <Form.Text className="text-muted">
              Select the bank or financial institution this statement is from
            </Form.Text>
          </Form.Group>

          <ColumnMappingTable
            analysis={analysisResult}
            columnMappings={columnMappings}
            onColumnMappingChange={handleColumnMappingChange}
            startRow={startRow}
            onStartRowChange={handleStartRowChange}
          />

          <ValidationMessages
            columnMappings={columnMappings}
            isValid={isMappingValid()}
          />

          <div className="d-flex justify-content-between mb-4">
            <Button
              variant="outline-secondary"
              onClick={handleReset}
            >
              Start Over
            </Button>

            <Button
              variant="primary"
              onClick={handleFinalUpload}
              disabled={!isMappingValid() || isUploading}
            >
              {isUploading ? 'Uploading...' : 'Finalize Upload'}
            </Button>
          </div>
        </>
      )}

      {uploadResult && (
        <Alert variant={uploadResult.success ? 'success' : 'danger'}>
          <Alert.Heading>{uploadResult.success ? 'Success!' : 'Error!'}</Alert.Heading>
          <p>{uploadResult.message}</p>
          {uploadResult.success && (
            <>
              <p>Transactions processed: {uploadResult.processed}</p>
              <p>Duplicate transactions skipped: {uploadResult.skipped}</p>
              <Button
                variant="primary"
                onClick={handleReset}
                className="mt-3"
              >
                Upload Another File
              </Button>
            </>
          )}
        </Alert>
      )}
    </Container>
  );
};

export default UploadPage;
