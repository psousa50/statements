import SourceSelector from './SourceSelector';
import StatisticsPanel from './StatisticsPanel';
import ActionButtons from './ActionButtons';
import ColumnMappingTable from './ColumnMappingTable';
import ValidationMessages from './ValidationMessages';
import { useUploadPageContext } from './UploadPageContext';
import type { Source } from '../../types';

interface AnalysisSummaryProps {
  sources: Source[];
}

export default function AnalysisSummary({ sources }: AnalysisSummaryProps) {
  const {
    analysisResult,
    sourceId,
    sourcePopupOpen,
    setSourceId,
    setSourcePopupOpen,
    columnMappings,
    setColumnMappings,
    startRow,
    setStartRow,
    headerRow,
    setHeaderRow,
    isValid,
    setFile,
    setAnalysisResult,
    setUploadResult,
    isUploading,
    setIsUploading,
  } = useUploadPageContext();

  const selectedSource = sources.find((s) => s.id === sourceId);

  return (
    <>
      {analysisResult && (
        <>
          <div style={{ width: '100%', display: 'flex', flexDirection: 'row', gap: '2rem', marginBottom: '2.5rem', alignItems: 'stretch', minHeight: 120 }}>
            <div style={{ flex: 2, display: 'flex', flexDirection: 'column', justifyContent: 'stretch', height: '100%' }}>
              <SourceSelector
                sources={sources}
                selectedSource={selectedSource}
                sourceId={sourceId}
                sourcePopupOpen={sourcePopupOpen}
                onButtonClick={() => setSourcePopupOpen(!sourcePopupOpen)}
                onOptionClick={setSourceId}
                onMouseEnter={() => {}}
                onMouseLeave={() => {}}
              />
            </div>
            <div style={{ flex: 4, display: 'flex', flexDirection: 'column', justifyContent: 'stretch', height: '100%' }}>
              <StatisticsPanel analysisResult={analysisResult} />
            </div>
          </div>
          <ColumnMappingTable
            analysis={analysisResult}
            columnMappings={columnMappings}
            onColumnMappingChange={(col, type) => setColumnMappings({ ...columnMappings, [col]: type })}
            startRow={startRow}
            onStartRowChange={setStartRow}
            headerRow={headerRow}
            onHeaderRowChange={setHeaderRow}
          />
          <ValidationMessages columnMappings={columnMappings} isValid={isValid} />
          <ActionButtons
            onStartOver={() => {
              setFile(undefined);
              setAnalysisResult(null);
              setUploadResult(null);
            }}
            onFinalize={() => setIsUploading(true)}
            isUploading={isUploading}
            isValid={isValid}
          />
        </>
      )}
    </>
  );
}
