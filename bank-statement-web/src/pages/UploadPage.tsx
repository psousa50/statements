import React, { useState, useCallback, useRef, useMemo } from 'react';
import {
  Container, Card, Button, Alert, Spinner,
  Table, Form, Row, Col, Badge
} from 'react-bootstrap';
import { useFileUpload, useFileAnalysis, useSources } from '../hooks/useQueries';
import { FileAnalysisResponse } from '../types';
import styles from './UploadPage.module.css';

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
  selectedSource: { name: string } | undefined;
}> = ({ analysis, selectedSource }) => {
  function formatDateVertical(dateStr?: string) {
    if (!dateStr) return 'N/A';
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
  }

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
                <h4>{selectedSource ? selectedSource.name : <span className="text-muted">No source selected</span>}</h4>
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
                <div style={{ fontSize: 20, fontWeight: 500, lineHeight: 1.2 }}>
                  <div>{formatDateVertical(analysis.date_range_start ?? undefined)}</div>
                  <div style={{ fontSize: 16, color: '#888' }}>to</div>
                  <div>{formatDateVertical(analysis.date_range_end ?? undefined)}</div>
                </div>
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
  headerRow: number;
  onHeaderRowChange: (headerRow: number) => void;
}> = ({ analysis, columnMappings, onColumnMappingChange, startRow, onStartRowChange, headerRow, onHeaderRowChange }) => {
  // Use the first row of preview_rows as the original columns
  const columns = analysis.preview_rows.length > 0 && analysis.preview_rows[headerRow] ? analysis.preview_rows[headerRow] : [];

  // Column mapping options
  const columnOptions = [
    { value: "date", label: "Date" },
    { value: "description", label: "Description" },
    { value: "amount", label: "Amount" },
    { value: "debit_amount", label: "Debit Amount" },
    { value: "credit_amount", label: "Credit Amount" },
    { value: "currency", label: "Currency" },
    { value: "balance", label: "Balance" },
    { value: "category", label: "Category (optional)" },
    { value: "ignore", label: "Ignore" }
  ];

  return (
    <Card className="mb-4">
      <Card.Header className="d-flex justify-content-between align-items-center">
        <h5 className="mb-0">Column Mapping</h5>
        <div className="d-flex gap-3">
          <Form.Group className="mb-0 d-flex align-items-center">
            <Form.Label htmlFor="header-row-input" className="me-2 mb-0">Header row:</Form.Label>
            <Form.Control
              id="header-row-input"
              type="number"
              min="0"
              value={headerRow}
              onChange={(e) => onHeaderRowChange(parseInt(e.target.value))}
              style={{ width: '80px' }}
            />
          </Form.Group>
          <Form.Group className="mb-0 d-flex align-items-center">
            <Form.Label htmlFor="start-row-input" className="me-2 mb-0">Data starts at row:</Form.Label>
            <Form.Control
              id="start-row-input"
              type="number"
              min="0"
              value={startRow}
              onChange={(e) => onStartRowChange(parseInt(e.target.value))}
              style={{ width: '80px' }}
            />
          </Form.Group>
        </div>
      </Card.Header>
      <Card.Body className="p-0">
        <div className="table-responsive">
          <Table bordered hover className={styles['table-sm']}>
            <thead>
              <tr>
                {columns.map((column, index) => (
                  <th key={index} className={`text-center ${columnMappings[column] !== 'ignore' ? 'bg-info bg-opacity-25 fw-bold' : ''}`}>
                    <Form.Select
                      size="sm"
                      value={columnMappings[column] || 'ignore'}
                      onChange={(e) => onColumnMappingChange(column, e.target.value)}
                      className={columnMappings[column] !== 'ignore' ? 'border-primary' : ''}
                    >
                      {columnOptions.map(option => (
                        <option key={option.value} value={option.value}>
                          {option.label}
                        </option>
                      ))}
                    </Form.Select>
                    <Badge bg={columnMappings[column] !== 'ignore' ? 'primary' : 'secondary'} className="mt-2 d-block">
                      {column}
                    </Badge>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {analysis.preview_rows.map((row, rowIndex) => {
                const isSpecialRow = rowIndex === headerRow || rowIndex === startRow;
                return (
                  <tr key={rowIndex}>
                    {columns.map((column, colIndex) => {
                      const value = colIndex < row.length ? row[colIndex] : '';
                      const isAssignedColumn = columnMappings[column] !== 'ignore';
                      const mappingType = columnMappings[column];
                      let displayValue = value;
                      let amountClass = '';
                      let alignClass = '';
                      if ((mappingType === 'debit_amount' || mappingType === 'credit_amount')) {
                        const num = typeof value === 'string' ? parseFloat(value.replace(/,/g, '')) : value;
                        if (!isNaN(num) && Number(num) === 0) displayValue = '';
                        alignClass = 'text-end';
                      }
                      if (mappingType === 'amount' && value !== '') {
                        const num = typeof value === 'string' ? parseFloat(value.replace(/,/g, '')) : value;
                        if (!isNaN(num)) {
                          if (num > 0) amountClass = 'text-success';
                          else if (num < 0) amountClass = 'text-danger';
                        }
                        alignClass = 'text-end';
                      }
                      if (mappingType === 'balance') {
                        alignClass = 'text-end';
                      }
                      return (
                        <td
                          key={colIndex}
                          className={`${rowIndex === headerRow ? styles['header-row-highlight'] : isAssignedColumn ? 'bg-info bg-opacity-10' : ''} ${isAssignedColumn ? 'fw-bold' : ''} ${amountClass} ${alignClass}`}
                        >
                          {displayValue}
                        </td>
                      );
                    })}
                  </tr>
                )
              })}
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
  const hasDateColumn = Object.values(columnMappings).includes('date');
  const hasDescriptionColumn = Object.values(columnMappings).includes('description');
  const hasAmountColumn = Object.values(columnMappings).includes('amount');
  const hasDebitAmountColumn = Object.values(columnMappings).includes('debit_amount');
  const hasCreditAmountColumn = Object.values(columnMappings).includes('credit_amount');

  const bothDebitCreditAssigned = hasDebitAmountColumn && hasCreditAmountColumn;
  const onlyOneDebitCreditAssigned = (hasDebitAmountColumn || hasCreditAmountColumn) && !(hasDebitAmountColumn && hasCreditAmountColumn);
  const hasAmountAndDebitCredit = hasAmountColumn && (hasDebitAmountColumn || hasCreditAmountColumn);

  const amountRequired = !bothDebitCreditAssigned;

  // Ensure each mapping type is assigned only once (excluding 'ignore' and 'category')
  const assignedTypes = Object.values(columnMappings).filter(
    v => v !== 'ignore' && v !== 'category'
  );
  const duplicates = assignedTypes.filter((v, i, arr) => arr.indexOf(v) !== i);
  const hasDuplicateAssignments = duplicates.length > 0;

  if (isValid) {
    return (
      <Alert variant="success" className="mb-4">
        <Alert.Heading>Ready to Upload</Alert.Heading>
        <p>Your column mappings look good! Click "Finalize Upload" to import your transactions.</p>
      </Alert>
    );
  }

  const hasIssues =
    !hasDateColumn ||
    !hasDescriptionColumn ||
    (amountRequired && !hasAmountColumn) ||
    onlyOneDebitCreditAssigned ||
    hasAmountAndDebitCredit ||
    hasDuplicateAssignments;

  return hasIssues ? (
    <Alert variant="warning" className="mb-4">
      <Alert.Heading>Please Fix the Following Issues:</Alert.Heading>
      <ul className="mb-0">
        {!hasDateColumn && (
          <li>Date column is required - please select which column contains transaction dates</li>
        )}
        {!hasDescriptionColumn && (
          <li>Description column is required - please select which column contains transaction descriptions</li>
        )}
        {amountRequired && !hasAmountColumn && (
          <li>Amount column is required unless both Debit and Credit columns are mapped</li>
        )}
        {onlyOneDebitCreditAssigned && (
          <li>If you assign either Debit or Credit column, you must assign both</li>
        )}
        {hasAmountAndDebitCredit && (
          <li>If using Debit and Credit columns, Amount column must not be assigned</li>
        )}
        {hasDuplicateAssignments && (
          <li>Each column type (except Ignore/Category) can only be assigned once</li>
        )}
      </ul>
    </Alert>
  ) : <div></div>;
};

// Main Upload Page component
const UploadPage: React.FC = () => {
  const [file, setFile] = useState<File | undefined>(undefined);
  const [sourceId, setSourceId] = useState<number | undefined>(undefined);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<FileAnalysisResponse | null>(null);
  const [columnMappings, setColumnMappings] = useState<Record<string, string>>({});
  const [startRow, setStartRow] = useState(0);
  const [headerRow, setHeaderRow] = useState(0);
  const [uploadResult, setUploadResult] = useState<{
    success: boolean;
    message: string;
    processed: number;
    skipped: number;
  } | null>(null);

  const { mutate: uploadFileMutation } = useFileUpload();
  const { mutate: analyzeFileMutation } = useFileAnalysis();
  const { data: sources, isLoading: isLoadingSources } = useSources();

  const selectedSource = sources?.find((s) => s.id === sourceId);

  // Handle file selection
  const handleFileSelected = useCallback(async (selectedFile: File) => {
    setFile(selectedFile);
    setIsAnalyzing(true);
    setAnalysisResult(null);
    setUploadResult(null);
    try {
      const fileContent = await new Promise<string>((resolve) => {
        const reader = new FileReader();
        reader.onloadend = () => {
          const base64 = reader.result as string;
          const base64Content = base64.split(',')[1];
          resolve(base64Content);
        };
        reader.readAsDataURL(selectedFile);
      });

      analyzeFileMutation(
        { fileContent, fileName: selectedFile.name },
        {
          onSuccess: (data) => {
            setAnalysisResult(data);
            const headerRow = data.statement_schema.header_row;
            const initialMappings: Record<string, string> = {};

            const columnNames = data.preview_rows.length > headerRow && data.preview_rows[headerRow] ? data.preview_rows[headerRow] : [];
            const columnMap = data.statement_schema.column_mapping;

            for (const column of columnNames) {
              initialMappings[column] = 'ignore';
            }

            if (columnMap.date && columnNames.includes(columnMap.date)) {
              initialMappings[columnMap.date] = 'date';
            }

            if (columnMap.description && columnNames.includes(columnMap.description)) {
              initialMappings[columnMap.description] = 'description';
            }

            if (columnMap.amount && columnNames.includes(columnMap.amount)) {
              initialMappings[columnMap.amount] = 'amount';
            }

            if (columnMap.debit_amount && columnNames.includes(columnMap.debit_amount)) {
              initialMappings[columnMap.debit_amount] = 'debit_amount';
            }

            if (columnMap.credit_amount && columnNames.includes(columnMap.credit_amount)) {
              initialMappings[columnMap.credit_amount] = 'credit_amount';
            }

            if (columnMap.currency && columnNames.includes(columnMap.currency)) {
              initialMappings[columnMap.currency] = 'currency';
            }

            if (columnMap.balance && columnNames.includes(columnMap.balance)) {
              initialMappings[columnMap.balance] = 'balance';
            }

            setColumnMappings(initialMappings);
            setStartRow(data.statement_schema.start_row);
            setHeaderRow(data.statement_schema.header_row || 0);
            setSourceId(data.statement_schema.source_id ?? undefined);
            setIsAnalyzing(false);
          },
          onError: (error) => {
            console.error('Error analyzing file:', error);
            setUploadResult({
              success: false,
              message: 'Error analyzing file. Please try again.',
              processed: 0,
              skipped: 0,
            });
            setIsAnalyzing(false);
          }
        }
      );
    } catch (error) {
      console.error('Error preparing file for analysis:', error);
      setUploadResult({
        success: false,
        message: 'Error preparing file for analysis. Please try again.',
        processed: 0,
        skipped: 0,
      });
      setIsAnalyzing(false);
    }
  }, [analyzeFileMutation]);

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

  // Handle header row change
  const handleHeaderRowChange = useCallback((newHeaderRow: number) => {
    if (Number.isNaN(newHeaderRow)) return;

    const originalColumnName = (column_name: string) => {
      const index = analysisResult?.preview_rows[headerRow].findIndex((col) => col === column_name);
      return index !== undefined ? analysisResult?.preview_rows[newHeaderRow][index] : column_name;
    }

    setHeaderRow(newHeaderRow);
    const newColumnMappings = Object.fromEntries(
      Object.entries(columnMappings).map(([key, value]) => [originalColumnName(key), value])
    );
    setColumnMappings(newColumnMappings);
  }, [analysisResult, headerRow, columnMappings]);

  // Handle source change
  const handleSourceChange = useCallback((e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value;
    const parsedValue = value ? parseInt(value) : undefined;
    setSourceId(parsedValue);
  }, []);

  // Check if mappings are valid
  const isValid = useMemo(() => {
    const mappingValues = Object.values(columnMappings);
    const hasDateColumn = mappingValues.includes('date');
    const hasDescriptionColumn = mappingValues.includes('description');
    const hasAmountColumn = mappingValues.includes('amount');
    const hasDebitAmountColumn = mappingValues.includes('debit_amount');
    const hasCreditAmountColumn = mappingValues.includes('credit_amount');

    const bothDebitCreditAssigned = hasDebitAmountColumn && hasCreditAmountColumn;
    const onlyOneDebitCreditAssigned = (hasDebitAmountColumn || hasCreditAmountColumn) && !(hasDebitAmountColumn && hasCreditAmountColumn);
    const hasAmountAndDebitCredit = hasAmountColumn && (hasDebitAmountColumn || hasCreditAmountColumn);

    const amountRequired = !bothDebitCreditAssigned;

    const assignedTypes = mappingValues.filter(v => v !== 'ignore' && v !== 'category');
    const duplicates = assignedTypes.filter((v, i, arr) => arr.indexOf(v) !== i);
    const hasDuplicateAssignments = duplicates.length > 0;

    return (
      hasDateColumn &&
      hasDescriptionColumn &&
      (!amountRequired ? true : hasAmountColumn) &&
      !onlyOneDebitCreditAssigned &&
      !hasAmountAndDebitCredit &&
      !hasDuplicateAssignments &&
      sourceId !== undefined
    );
  }, [columnMappings, sourceId]);

  // Handle final upload
  const handleFinalUpload = useCallback(async () => {
    if (!file || !analysisResult || !isValid) {
      return;
    }

    setIsUploading(true);

    // Pick column names from the header row selected by the user
    let headerColumns: string[] = [];
    if (analysisResult.preview_rows && analysisResult.preview_rows.length > headerRow) {
      headerColumns = analysisResult.preview_rows[headerRow];
    } else if (analysisResult.preview_rows.length > 0) {
      headerColumns = analysisResult.preview_rows[0];
    }

    // Build the updated column mapping: for each type, find the index of the column in the previous header row that was mapped to it, and assign the column at that index in the new header row
    const reversedColumnMappings = Object.entries(columnMappings)
      .map(([columnName, mappingType]) => [mappingType, columnName])
    const updatedMapping = Object.fromEntries(reversedColumnMappings);
    const updatedSchema = {
      ...analysisResult.statement_schema,
      start_row: startRow,
      header_row: headerRow,
      source_id: sourceId || analysisResult.statement_schema.source_id,
      column_mapping: updatedMapping
    };
    const payload = {
      statementSchema: updatedSchema,
      statement_id: analysisResult.file_id
    };

    uploadFileMutation(
      payload,
      {
        onSuccess: (data) => {
          setUploadResult({
            success: true,
            message: data.message,
            processed: data.transactions_processed,
            skipped: data.skipped_duplicates,
          });
          setFile(undefined);
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
  }, [analysisResult, sourceId, uploadFileMutation, isValid, startRow, headerRow, columnMappings, file]);

  // Reset the form
  const handleReset = useCallback(() => {
    setFile(undefined);
    setAnalysisResult(null);
    setColumnMappings({});
    setUploadResult(null);
    setSourceId(undefined);
    setHeaderRow(0);
    setStartRow(0);
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
          <AnalysisSummary analysis={analysisResult} selectedSource={selectedSource} />

          <Form.Group className="mb-4 d-flex align-items-center gap-2">
            <Form.Label htmlFor="source-select" className="mb-0">Source <span className="text-danger">*</span></Form.Label>
            <Form.Select
              id="source-select"
              value={sourceId || ''}
              onChange={handleSourceChange}
              disabled={isLoadingSources}
              isInvalid={analysisResult && !sourceId}
              required
              style={{ maxWidth: 340 }}
            >
              <option value="">Select a source</option>
              {sources?.map((source) => (
                <option key={source.id} value={source.id}>
                  {source.name}
                </option>
              ))}
            </Form.Select>
            {!sourceId && (
              <Form.Control.Feedback type="invalid">
                Please select a source. This is required to upload the statement.
              </Form.Control.Feedback>
            )}
            <Form.Text className="text-muted ms-2">
              Select the bank or financial institution this statement is from
            </Form.Text>
          </Form.Group>

          <ColumnMappingTable
            analysis={analysisResult}
            columnMappings={columnMappings}
            onColumnMappingChange={handleColumnMappingChange}
            startRow={startRow}
            onStartRowChange={handleStartRowChange}
            headerRow={headerRow}
            onHeaderRowChange={handleHeaderRowChange}
          />

          <ValidationMessages
            columnMappings={columnMappings}
            isValid={isValid}
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
              disabled={!isValid || isUploading}
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
