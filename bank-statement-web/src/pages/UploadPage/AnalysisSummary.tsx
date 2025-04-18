import React from 'react';
import { Card, Row, Col } from 'react-bootstrap';
import { FileAnalysisResponse } from '../../types';

interface AnalysisSummaryProps {
  analysis: FileAnalysisResponse;
  selectedSource: { name: string } | undefined;
}

function formatDateVertical(dateStr?: string | null) {
  if (!dateStr) return 'N/A';
  const date = new Date(dateStr);
  return date.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
}

const AnalysisSummary: React.FC<AnalysisSummaryProps> = ({ analysis, selectedSource }) => (
  <Card className="mb-4">
    <Card.Header>
      <h5 className="mb-0">Analysis Summary</h5>
    </Card.Header>
    <Card.Body>
      <Row>
        <Col md={3} className="mb-3">
          <Card className="h-100">
            <Card.Body className="text-center">
              <h6 className="text-muted">Source</h6>
              <h4>{selectedSource ? selectedSource.name : <span className="text-muted">No source selected</span>}</h4>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3} className="mb-3">
          <Card className="h-100">
            <Card.Body className="text-center">
              <h6 className="text-muted">Transactions</h6>
              <h4>{analysis.total_transactions}</h4>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3} className="mb-3">
          <Card className="h-100">
            <Card.Body className="text-center">
              <h6 className="text-muted">Total Amount</h6>
              <h4>{analysis.total_amount.toFixed(2)}</h4>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3} className="mb-3">
          <Card className="h-100">
            <Card.Body className="text-center">
              <h6 className="text-muted">Date Range</h6>
              <div style={{ fontSize: 20, fontWeight: 500, lineHeight: 1.2 }}>
                <div>{formatDateVertical(analysis.date_range_start ?? undefined)}</div>
                <div style={{ fontSize: 16, color: '#888' }}>to</div>
                <div>{formatDateVertical(analysis.date_range_end ?? undefined)}</div>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Card.Body>
  </Card>
);

export default AnalysisSummary;
