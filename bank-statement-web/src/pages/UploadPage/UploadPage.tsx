import React, { useCallback, useState } from 'react';
import { Alert, Button, Container } from 'react-bootstrap';
import { StatementAnalysisMutation, useSources, useStatementAnalysis, useStatementUpload } from '../../hooks/useQueries';
import type { UploadResult, StatementSchemaDefinition, StatementUploadResponse } from '../../types';
import type { UploadStatementMutation, UploadStatementRequest } from "../../hooks/useQueries";
import FileUploadZone from './FileUploadZone';
import AnalysisSummary from './AnalysisSummary';
import type { StatementAnalysisResponse } from '../../types';
import styles from './UploadPage.module.css';

export interface UploadFileSpec {
  statementId: string;
  statementSchema: StatementSchemaDefinition;
}


const UploadPage: React.FC = () => {
  const { data: sources } = useSources();
  const [sourceId, setSourceId] = useState<number | undefined>(undefined);
  const [isLoading, setIsLoading] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<StatementAnalysisResponse | null>(null);
  const [uploadResult, setUploadResult] = useState<UploadResult | null>(null);
  const [columnMappings, setColumnMappings] = useState<Record<string, string>>({});
  const [uploadFileSpec, setUploadFileSpec] = useState<UploadFileSpec | null>(null);

  const { mutateAsync: analyzeFileMutation } = useStatementAnalysis();
  const { mutateAsync: uploadFileMutation } = useStatementUpload();

  const handleFileSelected = useCallback(async (selectedFile: File) => {
    setIsLoading(true);
    try {
      const { analysisResult, initialMappings } = await performAnalyseStatement(selectedFile, analyzeFileMutation);
      setAnalysisResult(analysisResult);
      setColumnMappings(initialMappings);
      setUploadFileSpec({
        statementId: analysisResult.statementId,
        statementSchema: analysisResult.statementSchema
      });
      setSourceId(analysisResult.statementSchema.sourceId);
    } catch (error) {
      setUploadResult({
        success: false,
        message: `Error analyzing file. Please try again. ${error instanceof Error ? error.message : 'An unknown error occurred'}`,
        transactionsProcessed: 0,
        skippedDuplicates: 0,
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
      const { message, transactionsProcessed, skippedDuplicates } =
        await performFinalizeUpload(
          analysisResult,
          uploadFileSpec,
          sourceId,
          columnMappings,
          uploadFileMutation);
      setUploadResult({
        success: true,
        message,
        transactionsProcessed,
        skippedDuplicates,
      });
    } catch (error) {
      setUploadResult({
        success: false,
        message: error instanceof Error ? error.message : 'An error occurred during upload',
        transactionsProcessed: 0,
        skippedDuplicates: 0,
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
              <p>Transactions processed: {uploadResult.transactionsProcessed}</p>
              <p>Duplicate transactions skipped: {uploadResult.skippedDuplicates}</p>
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
        startRow: newStartRow
      }
    });
  }

  function handleHeaderRowChange(newHeaderRow: number) {
    if (!uploadFileSpec || Number.isNaN(newHeaderRow)) return;

    setUploadFileSpec({
      ...uploadFileSpec,
      statementSchema: {
        ...uploadFileSpec.statementSchema,
        headerRow: newHeaderRow
      }
    });

    const originalColumnName = (column_name: string) => {
      const index = analysisResult?.previewRows[uploadFileSpec.statementSchema.headerRow].findIndex((col) => col === column_name);
      return index !== undefined ? analysisResult?.previewRows[newHeaderRow][index] : column_name;
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

async function performAnalyseStatement(
  selectedFile: File,
  analyzeStatementMutation: StatementAnalysisMutation['mutateAsync'],
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
  const analysisResult = await analyzeStatementMutation({ fileContent, fileName: selectedFile.name });
  const headerRow = analysisResult.statementSchema.headerRow;
  const initialMappings: Record<string, string> = {};
  const columnNames = analysisResult.previewRows.length > headerRow && analysisResult.previewRows[headerRow] ? analysisResult.previewRows[headerRow] : [];
  const columnMap = analysisResult.statementSchema.columnMapping;
  for (const column of columnNames) {
    initialMappings[column] = 'ignore';
  }
  if (columnMap.date && columnNames.includes(columnMap.date)) initialMappings[columnMap.date] = 'date';
  if (columnMap.description && columnNames.includes(columnMap.description)) initialMappings[columnMap.description] = 'description';
  if (columnMap.amount && columnNames.includes(columnMap.amount)) initialMappings[columnMap.amount] = 'amount';
  if (columnMap.debitAmount && columnNames.includes(columnMap.debitAmount)) initialMappings[columnMap.debitAmount] = 'debit_amount';
  if (columnMap.creditAmount && columnNames.includes(columnMap.creditAmount)) initialMappings[columnMap.creditAmount] = 'credit_amount';
  if (columnMap.currency && columnNames.includes(columnMap.currency)) initialMappings[columnMap.currency] = 'currency';
  if (columnMap.balance && columnNames.includes(columnMap.balance)) initialMappings[columnMap.balance] = 'balance';

  return {
    analysisResult,
    initialMappings,
  }
}

async function performFinalizeUpload(
  analysisResult: StatementAnalysisResponse,
  uploadFileSpec: UploadFileSpec,
  sourceId: number | undefined,
  columnMappings: Record<string, string>,
  uploadFileMutation: UploadStatementMutation['mutateAsync'],
): Promise<StatementUploadResponse> {
  const reversedColumnMappings = Object.entries(columnMappings)
    .map(([columnName, mappingType]) => [mappingType, columnName]);
  const updatedMapping = Object.fromEntries(reversedColumnMappings);
  const updatedSchema: StatementSchemaDefinition = {
    ...analysisResult.statementSchema,
    startRow: uploadFileSpec.statementSchema.startRow,
    headerRow: uploadFileSpec.statementSchema.headerRow,
    sourceId,
    columnMapping: updatedMapping
  };
  const uploadFileParams: UploadStatementRequest = {
    statementId: uploadFileSpec.statementId,
    statementSchema: updatedSchema
  };
  return await uploadFileMutation(uploadFileParams);
}


export default UploadPage;
