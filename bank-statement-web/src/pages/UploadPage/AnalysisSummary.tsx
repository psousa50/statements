import SourceSelector from './SourceSelector';
import StatisticsPanel from './StatisticsPanel';
import ActionButtons from './ActionButtons';
import ColumnMappingTable from './ColumnMappingTable';
import ValidationMessages from './ValidationMessages';
import type { FileAnalysisResponse, Source } from '../../types';
import { useState } from 'react';
import { UploadFileSpec } from './UploadPage';

interface AnalysisSummaryProps {
  isLoading: boolean;
  sources: Source[];
  sourceId: number | undefined;
  setSourceId: (id: number | undefined) => void;
  analysisResult: FileAnalysisResponse;
  columnMappings: Record<string, string>;
  onColumnMappingChange: (column: string, type: string) => void;
  uploadFileSpec: UploadFileSpec;
  onHeaderRowChange: (newHeaderRow: number) => void;
  onStartRowChange: (newStartRow: number) => void;
  onFinalizeUpload: () => void;
  onStartOver: () => void;
}

export default function AnalysisSummary({
  isLoading,
  sources,
  sourceId,
  setSourceId,
  analysisResult,
  columnMappings,
  onColumnMappingChange,
  uploadFileSpec,
  onHeaderRowChange,
  onStartRowChange,
  onFinalizeUpload,
  onStartOver,
}: AnalysisSummaryProps) {
  const [sourcePopupOpen, setSourcePopupOpen] = useState(false);

  const selectedSource = sources.find((s) => s.id === sourceId);

  const isValid = mappingIsValid();

  return (
    <div style={{ width: '100%', display: 'flex', flexDirection: 'column', gap: '2rem', marginBottom: '2.5rem', alignItems: 'stretch', minHeight: 120 }}>
      <div style={{ display: 'flex', flexDirection: 'row', justifyContent: 'stretch', height: '100%', gap: '1rem' }}>
        <div style={{ flex: 2, display: 'flex', flexDirection: 'column', height: '100%' }}>
          <SourceSelector
            sources={sources}
            selectedSource={selectedSource}
            sourceId={sourceId}
            sourcePopupOpen={sourcePopupOpen}
            onButtonClick={() => setSourcePopupOpen(!sourcePopupOpen)}
            onOptionClick={setSourceId}
            onMouseEnter={() => { }}
            onMouseLeave={() => { }}
          />
        </div>
        <div style={{ flex: 4, display: 'flex', flexDirection: 'column', height: '100%' }}>
          <StatisticsPanel analysisResult={analysisResult} />
        </div>
      </div>

      <ColumnMappingTable
        analysisResult={analysisResult}
        columnMappings={columnMappings}
        onColumnMappingChange={onColumnMappingChange}
        startRow={uploadFileSpec.statementSchema.start_row}
        onStartRowChange={onStartRowChange}
        headerRow={uploadFileSpec.statementSchema.header_row}
        onHeaderRowChange={onHeaderRowChange}
      />
      <ValidationMessages columnMappings={columnMappings} isValid={isValid} />
      <ActionButtons
        onFinalize={onFinalizeUpload}
        onStartOver={onStartOver}
        isLoading={isLoading}
        isValid={isValid}
      />
    </div >
  )

  function mappingIsValid() {
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
    const isValid = (
      hasDateColumn &&
      hasDescriptionColumn &&
      (!amountRequired ? true : hasAmountColumn) &&
      !onlyOneDebitCreditAssigned &&
      !hasAmountAndDebitCredit &&
      !hasDuplicateAssignments &&
      sourceId !== undefined
    );
    return isValid;
  }
}
