import React from 'react';

type Props = {
  analysisResult: any;
};

export default function StatisticsPanel({ analysisResult }: Props) {
  return (
    <div data-testid="analysis-summary-panel" style={{
      width: '100%',
      border: '1px solid #ccc',
      padding: '1.2rem 2rem',
      marginBottom: '1.5rem',
      background: '#fff',
      boxSizing: 'border-box',
      fontSize: '1.1rem',
      fontFamily: 'inherit',
      height: '100%',
    }}>
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
