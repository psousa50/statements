import React from 'react';
import SourceSelector from './SourceSelector';
import StatisticsPanel from './StatisticsPanel';
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
  menuStyle: React.CSSProperties;
  menuItemStyle: (highlighted: boolean) => React.CSSProperties;
  fullWidthPanelStyle: React.CSSProperties;
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
  menuStyle,
  menuItemStyle,
  fullWidthPanelStyle,
}: AnalysisSummaryProps) {
  return (
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
          menuStyle={menuStyle}
          menuItemStyle={menuItemStyle}
          fullWidthPanelStyle={{ ...fullWidthPanelStyle, height: '100%' }}
        />
      </div>
      <div style={{ flex: 4, display: 'flex', flexDirection: 'column', justifyContent: 'stretch', height: '100%' }}>
        <StatisticsPanel analysisResult={analysis} fullWidthPanelStyle={{ ...fullWidthPanelStyle, height: '100%' }} />
      </div>
    </div>
  );
}
