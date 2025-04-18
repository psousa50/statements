import React, { createContext, useContext, useState, useCallback } from 'react';
import { FileAnalysisResponse } from '../../types';
import type { Source } from '../../types';
import { useStatementAnalysis, useStatementUpload } from '../../hooks/useQueries';

interface UploadPageContextType {
  file: File | undefined;
  setFile: (file: File | undefined) => void;
  sourceId: number | undefined;
  setSourceId: (id: number | undefined) => void;
  analysisResult: FileAnalysisResponse | null;
  setAnalysisResult: (result: FileAnalysisResponse | null) => void;
  columnMappings: Record<string, string>;
  setColumnMappings: (mappings: Record<string, string>) => void;
  startRow: number;
  setStartRow: (row: number) => void;
  headerRow: number;
  setHeaderRow: (row: number) => void;
  uploadResult: {
    success: boolean;
    message: string;
    processed: number;
    skipped: number;
  } | null;
  setUploadResult: (result: UploadPageContextType['uploadResult']) => void;
  sourcePopupOpen: boolean;
  setSourcePopupOpen: (open: boolean) => void;
  isAnalyzing: boolean;
  setIsAnalyzing: (value: boolean) => void;
  isUploading: boolean;
  setIsUploading: (value: boolean) => void;
  isValid: boolean;
  setIsValid: (value: boolean) => void;
  handleFileSelected: (file: File) => void;
}

const UploadPageContext = createContext<UploadPageContextType | undefined>(undefined);

export function useUploadPageContext(): UploadPageContextType {
  const ctx = useContext(UploadPageContext);
  if (!ctx) throw new Error('useUploadPageContext must be used within an UploadPageProvider');
  return ctx;
}

export const UploadPageProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { mutate: analyzeFileMutation } = useStatementAnalysis();

  const [file, setFile] = useState<File | undefined>(undefined);
  const [sourceId, setSourceId] = useState<number | undefined>(undefined);
  const [analysisResult, setAnalysisResult] = useState<FileAnalysisResponse | null>(null);
  const [columnMappings, setColumnMappings] = useState<Record<string, string>>({});
  const [startRow, setStartRow] = useState(0);
  const [headerRow, setHeaderRow] = useState(0);
  const [uploadResult, setUploadResult] = useState<UploadPageContextType['uploadResult']>(null);
  const [sourcePopupOpen, setSourcePopupOpen] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [isValid, setIsValid] = useState(false);

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

  const value: UploadPageContextType = {
    file, setFile,
    sourceId, setSourceId,
    analysisResult, setAnalysisResult,
    columnMappings, setColumnMappings,
    startRow, setStartRow,
    headerRow, setHeaderRow,
    uploadResult, setUploadResult,
    sourcePopupOpen, setSourcePopupOpen,
    isAnalyzing, setIsAnalyzing,
    isUploading, setIsUploading,
    isValid, setIsValid,
    handleFileSelected,
  };

  return (
    <UploadPageContext.Provider value={value}>
      {children}
    </UploadPageContext.Provider>
  );
};
