import React, { useState, useCallback, useMemo } from 'react';
import { Container, Button, Alert, Form } from 'react-bootstrap';
import { useStatementUpload, useStatementAnalysis, useSources } from '../../hooks/useQueries';
import { FileAnalysisResponse } from '../../types';
import type { Source } from '../../types';
import FileUploadZone from './FileUploadZone';
import AnalysisSummary from './AnalysisSummary';
import ColumnMappingTable from './ColumnMappingTable';
import ValidationMessages from './ValidationMessages';
import styles from './UploadPage.module.css';

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

  const { mutate: uploadFileMutation } = useStatementUpload();
  const { mutate: analyzeFileMutation } = useStatementAnalysis();
  const { data: sources, isLoading: isLoadingSources } = useSources();

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
    setHeaderRow(newHeaderRow);
  }, []);

  const handleSourceChange = useCallback((e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value;
    const parsedValue = value ? parseInt(value) : undefined;
    setSourceId(parsedValue);
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

  return (
    <Container className={styles.uploadPageContainer}>
      {!file && !analysisResult && !uploadResult && (
        <FileUploadZone onFileSelected={handleFileSelected} isLoading={isAnalyzing} />
      )}
      {analysisResult && (
        <>
          <Form.Group className="mb-3">
            <Form.Label htmlFor="source-select" className="mb-0">Source <span className="text-danger">*</span></Form.Label>
            <Form.Select id="source-select" value={sourceId ?? ''} onChange={handleSourceChange} disabled={isLoadingSources}>
              <option value="">Select a source</option>
              {sources?.map((source: Source) => (
                <option key={source.id} value={source.id}>{source.name}</option>
              ))}
            </Form.Select>
          </Form.Group>
          <AnalysisSummary analysis={analysisResult} selectedSource={selectedSource} />
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
        </>
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
