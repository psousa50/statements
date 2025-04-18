import React from 'react';

type Props = {
  analysisResult: any;
  fullWidthPanelStyle: React.CSSProperties;
};

export default function StatisticsPanel({ analysisResult, fullWidthPanelStyle }: Props) {
  return (
    <div data-testid="analysis-summary-panel" style={fullWidthPanelStyle}>
      <div style={{ display: 'flex', flexDirection: 'row', justifyContent: 'space-between' }}>
        <span>Number of Transactions:</span>
        <span>{analysisResult.num_transactions?.toLocaleString?.() ?? analysisResult.analysis?.num_transactions?.toLocaleString?.() ?? ''}</span>
      </div>
      <div style={{ display: 'flex', flexDirection: 'row', justifyContent: 'space-between' }}>
        <span>Total amount</span>
        <span>: {analysisResult.currency ?? analysisResult.analysis?.currency ?? ''} {analysisResult.total_amount ?? analysisResult.analysis?.total_amount ?? ''}</span>
      </div>
      <div style={{ marginTop: 10 }}>From {analysisResult.start_date ?? analysisResult.analysis?.start_date ?? ''} to {analysisResult.end_date ?? analysisResult.analysis?.end_date ?? ''}</div>
    </div>
  );
}
