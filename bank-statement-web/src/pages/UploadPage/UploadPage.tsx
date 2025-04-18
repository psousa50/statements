import React, { useState, useCallback, useMemo } from 'react';
import { Container, Button, Alert, Form, Spinner } from 'react-bootstrap';
import { useSources, useStatementAnalysis, useStatementUpload } from '../../hooks/useQueries';
import { FileAnalysisResponse } from '../../types';
import type { Source } from '../../types';
import FileUploadZone from './FileUploadZone';
import AnalysisSummary from './AnalysisSummary';
import ColumnMappingTable from './ColumnMappingTable';
import ValidationMessages from './ValidationMessages';
import styles from './UploadPage.module.css';

const UploadPage: React.FC = () => {
  const { mutate: uploadFileMutation } = useStatementUpload();
  const { mutate: analyzeFileMutation } = useStatementAnalysis();
  const { data: sources, isLoading: isLoadingSources } = useSources();

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

  const [sourcePopupOpen, setSourcePopupOpen] = useState(false);

  const selectedSource = sources?.find((s: Source) => s.id === sourceId);

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
          onSuccess: (data: FileAnalysisResponse) => {
            setAnalysisResult(data);
            const headerRow = data.statement_schema.header_row;
            const initialMappings: Record<string, string> = {};
            const columnNames = data.preview_rows.length > headerRow && data.preview_rows[headerRow] ? data.preview_rows[headerRow] : [];
            const columnMap = data.statement_schema.column_mapping;
            for (const column of columnNames) {
              initialMappings[column] = 'ignore';
            }
            if (columnMap.date && columnNames.includes(columnMap.date)) initialMappings[columnMap.date] = 'date';
            if (columnMap.description && columnNames.includes(columnMap.description)) initialMappings[columnMap.description] = 'description';
            if (columnMap.amount && columnNames.includes(columnMap.amount)) initialMappings[columnMap.amount] = 'amount';
            if (columnMap.debit_amount && columnNames.includes(columnMap.debit_amount)) initialMappings[columnMap.debit_amount] = 'debit_amount';
            if (columnMap.credit_amount && columnNames.includes(columnMap.credit_amount)) initialMappings[columnMap.credit_amount] = 'credit_amount';
            if (columnMap.currency && columnNames.includes(columnMap.currency)) initialMappings[columnMap.currency] = 'currency';
            if (columnMap.balance && columnNames.includes(columnMap.balance)) initialMappings[columnMap.balance] = 'balance';
            setColumnMappings(initialMappings);
            setStartRow(data.statement_schema.start_row);
            setHeaderRow(data.statement_schema.header_row || 0);
            setSourceId(data.statement_schema.source_id ?? undefined);
            setIsAnalyzing(false);
          },
          onError: (error: unknown) => {
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
      setUploadResult({
        success: false,
        message: 'Error preparing file for analysis. Please try again.',
        processed: 0,
        skipped: 0,
      });
      setIsAnalyzing(false);
    }
  }, [analyzeFileMutation]);

  const handleColumnMappingChange = useCallback((columnName: string, mappingType: string) => {
    setColumnMappings(prevMappings => {
      if (mappingType === 'ignore') {
        return { ...prevMappings, [columnName]: 'ignore' };
      }
      const prevAssignment = prevMappings[columnName];
      const existingColumn = Object.entries(prevMappings).find(
        ([col, type]) => type === mappingType
      )?.[0];
      const newMappings = { ...prevMappings, [columnName]: mappingType };
      if (existingColumn && existingColumn !== columnName) {
        newMappings[existingColumn] = prevAssignment || 'ignore';
      }
      return newMappings;
    });
  }, []);

  const handleStartRowChange = useCallback((newStartRow: number) => {
    setStartRow(newStartRow);
  }, []);

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

  const handleSourceButtonClick = useCallback(() => {
    setSourcePopupOpen((open) => !open);
  }, []);

  const handleSourceOptionClick = useCallback((id: number) => {
    setSourceId(id);
    setSourcePopupOpen(false);
  }, []);

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

  const handleFinalUpload = useCallback(async () => {
    if (!file || !analysisResult || !isValid) {
      return;
    }
    setIsUploading(true);
    const reversedColumnMappings = Object.entries(columnMappings)
      .map(([columnName, mappingType]) => [mappingType, columnName]);
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
      statement_id: analysisResult.statement_id
    };
    uploadFileMutation(
      payload,
      {
        onSuccess: (data: { message: string; transactions_processed: number; skipped_duplicates: number }) => {
          setUploadResult({
            success: true,
            message: data.message,
            processed: data.transactions_processed,
            skipped: data.skipped_duplicates,
          });
          setFile(undefined);
          setAnalysisResult(null);
        },
        onError: (error: unknown) => {
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

  const handleReset = useCallback(() => {
    setFile(undefined);
    setAnalysisResult(null);
    setColumnMappings({});
    setUploadResult(null);
    setSourceId(undefined);
    setHeaderRow(0);
    setStartRow(0);
  }, []);

  const fullWidthPanelStyle: React.CSSProperties = {
    width: '100%',
    border: '1px solid #ccc',
    padding: '1.2rem 2rem',
    marginBottom: '1.5rem',
    background: '#fff',
    boxSizing: 'border-box',
    fontSize: '1.1rem',
    fontFamily: 'inherit',
  };
  const menuStyle: React.CSSProperties = {
    position: 'absolute',
    left: '100%',
    top: 0,
    minWidth: 180,
    background: '#fff',
    border: '1px solid #ccc',
    boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
    zIndex: 100,
    padding: 0,
    margin: 0,
    listStyle: 'none',
  };
  const menuItemStyle = (highlighted: boolean): React.CSSProperties => ({
    padding: '0.7rem 1.5rem',
    background: highlighted ? '#f0f4fa' : '#fff',
    cursor: 'pointer',
    fontWeight: 500,
    color: '#222',
    border: 'none',
    outline: 'none',
    width: '100%',
    textAlign: 'left',
  });

  const [hoveredSource, setHoveredSource] = useState<number | null>(null);

  return (
    <Container className={styles.uploadPageContainer}>
      {isAnalyzing && (
        <div style={{ display: 'flex', justifyContent: 'center', margin: '2rem 0' }}>
          <Spinner animation="border" role="status" aria-busy="true" data-testid="loading" style={{ width: 48, height: 48 }} />
        </div>
      )}
      {!file && !analysisResult && !uploadResult && (
        <FileUploadZone onFileSelected={handleFileSelected} isLoading={isAnalyzing} />
      )}
      {analysisResult && (
        <div>
          <div style={{ width: '100%', display: 'flex', flexDirection: 'column', gap: '1.2rem', marginBottom: '2.5rem' }}>
            <div data-testid="source-selector-panel" style={fullWidthPanelStyle}>
              <div style={{ position: 'relative', display: 'inline-block' }}>
                <Button
                  data-testid="source-selector-btn"
                  variant="outline-secondary"
                  aria-haspopup="menu"
                  aria-expanded={sourcePopupOpen}
                  onClick={handleSourceButtonClick}
                  style={{ minWidth: 180 }}
                >
                  Source: {selectedSource ? selectedSource.name : ''}
                </Button>
                {sourcePopupOpen && (
                  <ul
                    data-testid="source-selector-menu"
                    role="menu"
                    style={menuStyle}
                  >
                    {sources?.map((source: Source) => (
                      <li
                        key={source.id}
                        role="menuitem"
                        aria-selected={sourceId === source.id}
                        tabIndex={0}
                        style={menuItemStyle(hoveredSource === source.id)}
                        onMouseEnter={() => setHoveredSource(source.id)}
                        onMouseLeave={() => setHoveredSource(null)}
                        onClick={() => handleSourceOptionClick(source.id)}
                        onKeyDown={e => { if (e.key === 'Enter' || e.key === ' ') handleSourceOptionClick(source.id); }}
                        className={hoveredSource === source.id ? 'highlighted' : ''}
                      >
                        {source.name}
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            </div>
            <div data-testid="analysis-summary-panel" style={fullWidthPanelStyle}>
              <div style={{ display: 'flex', flexDirection: 'row', justifyContent: 'space-between' }}>
                <span>Number of Transactions:</span>
                <span>{(analysisResult as any).num_transactions?.toLocaleString?.() ?? (analysisResult as any).analysis?.num_transactions?.toLocaleString?.() ?? ''}</span>
              </div>
              <div style={{ display: 'flex', flexDirection: 'row', justifyContent: 'space-between' }}>
                <span>Total amount</span>
                <span>: {(analysisResult as any).currency ?? (analysisResult as any).analysis?.currency ?? ''} {(analysisResult as any).total_amount ?? (analysisResult as any).analysis?.total_amount ?? ''}</span>
              </div>
              <div style={{ marginTop: 10 }}>From {(analysisResult as any).start_date ?? (analysisResult as any).analysis?.start_date ?? ''} to {(analysisResult as any).end_date ?? (analysisResult as any).analysis?.end_date ?? ''}</div>
            </div>
          </div>
          <ColumnMappingTable
            analysis={analysisResult}
            columnMappings={columnMappings}
            onColumnMappingChange={handleColumnMappingChange}
            startRow={startRow}
            onStartRowChange={handleStartRowChange}
            headerRow={headerRow}
            onHeaderRowChange={handleHeaderRowChange}
          />
          <ValidationMessages columnMappings={columnMappings} isValid={isValid} />
          <div className="d-flex justify-content-between mb-4">
            <Button
              variant="outline-secondary"
              onClick={handleReset}
            >
              Start Over
            </Button>
            <div className="ms-auto">
              <Button
                variant="primary"
                onClick={handleFinalUpload}
                disabled={!isValid || isUploading}
              >
                {isUploading ? 'Uploading...' : 'Finalize Upload'}
              </Button>
            </div>
          </div>
          {uploadResult && (
            <Alert variant={uploadResult.success ? 'success' : 'danger'} className="mb-0">
              {uploadResult.message} Processed: {uploadResult.processed} Skipped: {uploadResult.skipped}
            </Alert>
          )}
        </div>
      )}
      {uploadResult && !analysisResult && (
        <Alert variant={uploadResult.success ? 'success' : 'danger'} className="mb-4" role="alert">
          <Alert.Heading>{uploadResult.success ? 'Success!' : 'Error!'}</Alert.Heading>
          <p>{uploadResult.message}</p>
          {uploadResult.success && (
            <>
              <p>Transactions processed: {uploadResult.processed}</p>
              <p>Duplicate transactions skipped: {uploadResult.skipped}</p>
            </>
          )}
          <Button
            variant="primary"
            onClick={handleReset}
            className="mt-3"
          >
            Upload Another File
          </Button>
        </Alert>
      )}
    </Container>
  );
};

export default UploadPage;
