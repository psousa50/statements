import { FileAnalysisResponse } from '../../types';

type Props = {
  analysisResult: FileAnalysisResponse;
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
        <span>{analysisResult.total_transactions.toLocaleString()}</span>
      </div>
      <div style={{ display: 'flex', flexDirection: 'row', justifyContent: 'space-between' }}>
        <span>Total amount:</span>
        <span>EUR {analysisResult.total_amount.toLocaleString()}</span>
      </div>
      <div style={{ marginTop: 10 }}>From {formatDate(analysisResult.date_range_start)} to {formatDate(analysisResult.date_range_end)}</div>
    </div>
  );

  function formatDate(date: string | null): string {
    return date ? new Date(date).toISOString().split('T')[0] : '';
  }
}
