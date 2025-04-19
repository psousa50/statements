import React, { useCallback, useState } from 'react';
import { Alert, Button, Container } from 'react-bootstrap';
import { StatementAnalysisMutation, useSources, useStatementAnalysis, useStatementUpload } from '../../hooks/useQueries';
import type { UploadResult, StatementSchemaDefinition, FileUploadResponse } from '../../types';
import type { UploadFileMutation } from "../../hooks/useQueries";
import FileUploadZone from './FileUploadZone';
import AnalysisSummary from './AnalysisSummary';
import type { FileAnalysisResponse } from '../../types';
import styles from './UploadPage.module.css';

export interface UploadFileSpec {
  statementId: string;
  statementSchema: StatementSchemaDefinition;
}


const UploadPage: React.FC = () => {
  const { data: sources } = useSources();
  const [sourceId, setSourceId] = useState<number | undefined>(undefined);
  const [isLoading, setIsLoading] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<FileAnalysisResponse | null>(null);
  const [uploadResult, setUploadResult] = useState<UploadResult | null>(null);
  const [columnMappings, setColumnMappings] = useState<Record<string, string>>({});
  const [uploadFileSpec, setUploadFileSpec] = useState<UploadFileSpec | null>(null);

  const { mutateAsync: analyzeFileMutation } = useStatementAnalysis();
  const { mutateAsync: uploadFileMutation } = useStatementUpload();

  const handleFileSelected = useCallback(async (selectedFile: File) => {
    setIsLoading(true);
    try {
      const { analysisResult, initialMappings } = await performFileSelected(selectedFile, analyzeFileMutation);
      setAnalysisResult(analysisResult);
      setColumnMappings(initialMappings);
      setUploadFileSpec({
        statementId: analysisResult.statement_id,
        statementSchema: analysisResult.statement_schema
      });
      setSourceId(analysisResult.statement_schema.source_id);
    } catch (error) {
      setUploadResult({
        success: false,
        message: 'Error analyzing file. Please try again.',
        processed: 0,
        skipped: 0,
      });
    }
    finally {
      setIsLoading(false);
    }
  }, [analyzeFileMutation]);

  const handleFinalizeUpload = useCallback(async () => {
    if (!analysisResult || !uploadFileSpec || !sourceId || !columnMappings) {
      return;
    }
    setIsLoading(true);
    try {
      const { message, transactions_processed, skipped_duplicates } =
        await performFinalizeUpload(
          analysisResult,
          uploadFileSpec,
          sourceId,
          columnMappings,
          uploadFileMutation);
      setUploadResult({
        success: true,
        message,
        processed: transactions_processed,
        skipped: skipped_duplicates,
      });
    } catch (error) {
      setUploadResult({
        success: false,
        message: error instanceof Error ? error.message : 'An error occurred during upload',
        processed: 0,
        skipped: 0,
      });
    }
    finally {
      setIsLoading(false);
      setAnalysisResult(null);
      setUploadFileSpec(null);
    }
  }, [analysisResult, uploadFileSpec, sourceId, columnMappings, uploadFileMutation]);

  return (
    <Container className={styles.uploadPageContainer}>
      {(!analysisResult && !uploadResult) && (
        <FileUploadZone onFileSelected={handleFileSelected} isLoading={isLoading} />
      )}
      {analysisResult && sources && uploadFileSpec && (
        <AnalysisSummary
          isLoading={isLoading}
          sources={sources}
          sourceId={sourceId}
          setSourceId={setSourceId}
          analysisResult={analysisResult}
          columnMappings={columnMappings}
          onColumnMappingChange={handleColumnMappingChange}
          uploadFileSpec={uploadFileSpec}
          onHeaderRowChange={handleHeaderRowChange}
          onStartRowChange={handleStartRowChange}
          onFinalizeUpload={handleFinalizeUpload}
          onStartOver={handleStartOver}
        />
      )}
      {uploadResult && (
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
            onClick={handleStartOver}
            className="mt-3"
          >
            Upload Another File
          </Button>
        </Alert>
      )}
    </Container>
  );


  function handleStartOver() {
    setAnalysisResult(null);
    setUploadResult(null);
    setColumnMappings({});
    setSourceId(undefined);
    setUploadFileSpec(null);
  };


  function handleStartRowChange(newStartRow: number) {
    if (!uploadFileSpec) return;
    setUploadFileSpec({
      ...uploadFileSpec,
      statementSchema: {
        ...uploadFileSpec.statementSchema,
        start_row: newStartRow
      }
    });
  }

  function handleHeaderRowChange(newHeaderRow: number) {
    if (!uploadFileSpec || Number.isNaN(newHeaderRow)) return;

    setUploadFileSpec({
      ...uploadFileSpec,
      statementSchema: {
        ...uploadFileSpec.statementSchema,
        header_row: newHeaderRow
      }
    });

    const originalColumnName = (column_name: string) => {
      const index = analysisResult?.preview_rows[uploadFileSpec.statementSchema.header_row].findIndex((col) => col === column_name);
      return index !== undefined ? analysisResult?.preview_rows[newHeaderRow][index] : column_name;
    }
    const newColumnMappings = Object.fromEntries(
      Object.entries(columnMappings).map(([key, value]) => [originalColumnName(key), value])
    );
    setColumnMappings(newColumnMappings);
  }

  function handleColumnMappingChange(columnName: string, mappingType: string) {
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
  }


};

async function performFileSelected(
  selectedFile: File,
  analyzeFileMutation: StatementAnalysisMutation['mutateAsync'],
) {
  const fileContent = await new Promise<string>((resolve) => {
    const reader = new FileReader();
    reader.onloadend = () => {
      const base64 = reader.result as string;
      const base64Content = base64.split(',')[1];
      resolve(base64Content);
    };
    reader.readAsDataURL(selectedFile);
  });
  const analysisResult = await analyzeFileMutation({ fileContent, fileName: selectedFile.name });
  const headerRow = analysisResult.statement_schema.header_row;
  const initialMappings: Record<string, string> = {};
  const columnNames = analysisResult.preview_rows.length > headerRow && analysisResult.preview_rows[headerRow] ? analysisResult.preview_rows[headerRow] : [];
  const columnMap = analysisResult.statement_schema.column_mapping;
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

  return {
    analysisResult,
    initialMappings,
  }
}

async function performFinalizeUpload(
  analysisResult: FileAnalysisResponse,
  uploadFileSpec: UploadFileSpec,
  sourceId: number | undefined,
  columnMappings: Record<string, string>,
  uploadFileMutation: UploadFileMutation['mutateAsync'],
): Promise<FileUploadResponse> {
  const reversedColumnMappings = Object.entries(columnMappings)
    .map(([columnName, mappingType]) => [mappingType, columnName]);
  const updatedMapping = Object.fromEntries(reversedColumnMappings);
  const updatedSchema = {
    ...analysisResult.statement_schema,
    start_row: uploadFileSpec.statementSchema.start_row,
    header_row: uploadFileSpec.statementSchema.header_row,
    source_id: sourceId,
    column_mapping: updatedMapping
  };
  const uploadFileParams = {
    statement_id: uploadFileSpec.statementId,
    statement_schema: updatedSchema
  };
  return await uploadFileMutation(uploadFileParams);
}


export default UploadPage;
