import React from 'react';
import SourceSelector from './SourceSelector';
import StatisticsPanel from './StatisticsPanel';
import ActionButtons from './ActionButtons';
import ColumnMappingTable from './ColumnMappingTable';
import ValidationMessages from './ValidationMessages';
import { FileAnalysisResponse } from '../../types';
import type { Source } from '../../types';

interface AnalysisSummaryProps {
  analysis: FileAnalysisResponse;
  selectedSource: Source | undefined;
  sources: Source[];
  sourceId?: number;
  sourcePopupOpen: boolean;
  hoveredSource: number | null;
  onSourceButtonClick: () => void;
  onSourceOptionClick: (id: number) => void;
  onSourceMouseEnter: (id: number) => void;
  onSourceMouseLeave: () => void;
  columnMappings: Record<string, string>;
  onColumnMappingChange: (columnName: string, mappingType: string) => void;
  startRow: number;
  onStartRowChange: (newStartRow: number) => void;
  headerRow: number;
  onHeaderRowChange: (newHeaderRow: number) => void;
  isValid: boolean;
  onStartOver: () => void;
  onFinalize: () => void;
  isUploading: boolean;
}

export default function AnalysisSummary({
  analysis,
  selectedSource,
  sources,
  sourceId,
  sourcePopupOpen,
  hoveredSource,
  onSourceButtonClick,
  onSourceOptionClick,
  onSourceMouseEnter,
  onSourceMouseLeave,
  columnMappings,
  onColumnMappingChange,
  startRow,
  onStartRowChange,
  headerRow,
  onHeaderRowChange,
  isValid,
  onStartOver,
  onFinalize,
  isUploading,
}: AnalysisSummaryProps) {
  const fullWidthPanelStyle: React.CSSProperties = {
    width: '100%',
    border: '1px solid #ccc',
    padding: '1.2rem 2rem',
    marginBottom: '1.5rem',
    background: '#fff',
    boxSizing: 'border-box',
    fontSize: '1.1rem',
    fontFamily: 'inherit',
    height: '100%',
  };
  return (
    <>
      <div style={{ width: '100%', display: 'flex', flexDirection: 'row', gap: '2rem', marginBottom: '2.5rem', alignItems: 'stretch', minHeight: 120 }}>
        <div style={{ flex: 2, display: 'flex', flexDirection: 'column', justifyContent: 'stretch', height: '100%' }}>
          <SourceSelector
            sources={sources}
            selectedSource={selectedSource}
            sourceId={sourceId}
            sourcePopupOpen={sourcePopupOpen}
            hoveredSource={hoveredSource}
            onButtonClick={onSourceButtonClick}
            onOptionClick={onSourceOptionClick}
            onMouseEnter={onSourceMouseEnter}
            onMouseLeave={onSourceMouseLeave}
          />
        </div>
        <div style={{ flex: 4, display: 'flex', flexDirection: 'column', justifyContent: 'stretch', height: '100%' }}>
          <StatisticsPanel analysisResult={analysis} />
        </div>
      </div>
      <ColumnMappingTable
        analysis={analysis}
        columnMappings={columnMappings}
        onColumnMappingChange={onColumnMappingChange}
        startRow={startRow}
        onStartRowChange={onStartRowChange}
        headerRow={headerRow}
        onHeaderRowChange={onHeaderRowChange}
      />
      <ValidationMessages columnMappings={columnMappings} isValid={isValid} />
      <ActionButtons
        onStartOver={onStartOver}
        onFinalize={onFinalize}
        isUploading={isUploading}
        isValid={isValid}
      />
    </>
  );
}
