import React from 'react';
import { Card, Table, Form, Badge } from 'react-bootstrap';
import { StatementAnalysisResponse } from '../../types';
import styles from './UploadPage.module.css';

interface ColumnMappingTableProps {
  analysisResult: StatementAnalysisResponse;
  columnMappings: Record<string, string>;
  onColumnMappingChange: (columnName: string, mappingType: string) => void;
  startRow: number;
  onStartRowChange: (startRow: number) => void;
  headerRow: number;
  onHeaderRowChange: (headerRow: number) => void;
}

const ColumnMappingTable: React.FC<ColumnMappingTableProps> = ({
  analysisResult: analysis,
  columnMappings,
  onColumnMappingChange,
  startRow,
  onStartRowChange,
  headerRow,
  onHeaderRowChange
}) => {
  const columns =
    analysis.previewRows.length > 0 && analysis.previewRows[headerRow]
      ? analysis.previewRows[headerRow]
      : [];

  const columnOptions = [
    { value: "ignore", label: "Ignore" },
    { value: "date", label: "Date" },
    { value: "description", label: "Description" },
    { value: "amount", label: "Amount" },
    { value: "debit_amount", label: "Debit Amount" },
    { value: "credit_amount", label: "Credit Amount" },
    { value: "currency", label: "Currency" },
    { value: "balance", label: "Balance" },
    { value: "category", label: "Category (optional)" },
  ];

  const handleHeaderRowChange = (value: number) => {
    if (value < startRow) {
      onHeaderRowChange(value);
    }
  };

  const handleStartRowChange = (value: number) => {
    if (value > headerRow) {
      onStartRowChange(value);
    }
  };

  return (
    <Card className="mb-4">
      <Card.Header className="d-flex justify-content-between align-items-center">
        <h5 className="mb-0">Column Mapping</h5>
        <div className="d-flex gap-3">
          <Form.Group className="mb-0 d-flex align-items-center">
            <Form.Label htmlFor="header-row-input" className="me-2 mb-0">Header row:</Form.Label>
            <Form.Control
              id="header-row-input"
              type="number"
              min="0"
              value={headerRow}
              onChange={(e) => handleHeaderRowChange(parseInt(e.target.value))}
              style={{ width: '80px' }}
            />
          </Form.Group>
          <Form.Group className="mb-0 d-flex align-items-center">
            <Form.Label htmlFor="start-row-input" className="me-2 mb-0">Data starts at row:</Form.Label>
            <Form.Control
              id="start-row-input"
              type="number"
              min="0"
              value={startRow}
              onChange={(e) => handleStartRowChange(parseInt(e.target.value))}
              style={{ width: '80px' }}
            />
          </Form.Group>
        </div>
      </Card.Header>
      <Card.Body className="p-0">
        <div className="table-responsive">
          <Table bordered hover className={styles['table-sm']}>
            <thead>
              <tr>
                {columns.map((column, index) => (
                  <th key={index} className={`text-center ${columnMappings[column] !== 'ignore' ? 'bg-info bg-opacity-25 fw-bold' : ''}`}>
                    <Form.Select
                      size="sm"
                      value={columnMappings[column] || 'ignore'}
                      onChange={(e) => onColumnMappingChange(column, e.target.value)}
                      className={columnMappings[column] !== 'ignore' ? 'border-primary' : ''}
                    >
                      {columnOptions.map(option => (
                        <option key={option.value} value={option.value}>
                          {option.label}
                        </option>
                      ))}
                    </Form.Select>
                    <Badge bg={columnMappings[column] !== 'ignore' ? 'primary' : 'secondary'} className="mt-2 d-block">
                      {column}
                    </Badge>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {analysis.previewRows.map((row, rowIndex) => {
                const isStartRow = rowIndex === startRow;
                const isHeaderRow = rowIndex === headerRow;
                return (
                  <tr key={rowIndex} className={`${isStartRow ? styles['start-row-highlight'] : ''} ${isHeaderRow ? styles['header-row-highlight'] : ''}`}>
                    {columns.map((column, colIndex) => {
                      const value = colIndex < row.length ? row[colIndex] : '';
                      const isAssignedColumn = columnMappings[column] !== 'ignore';
                      const mappingType = columnMappings[column];
                      let displayValue = value;
                      let amountClass = '';
                      let alignClass = '';
                      if ((mappingType === 'debit_amount' || mappingType === 'credit_amount')) {
                        const num = typeof value === 'string' ? parseFloat(value.replace(/,/g, '')) : value;
                        if (!isNaN(num) && Number(num) === 0) displayValue = '';
                        alignClass = 'text-end';
                      }
                      if (mappingType === 'amount' && value !== '') {
                        const num = typeof value === 'string' ? parseFloat(value.replace(/,/g, '')) : value;
                        if (!isNaN(num)) {
                          if (num > 0) amountClass = 'text-success';
                          else if (num < 0) amountClass = 'text-danger';
                        }
                        alignClass = 'text-end';
                      }
                      if (mappingType === 'balance') {
                        alignClass = 'text-end';
                      }
                      return (
                        <td
                          key={colIndex}
                          className={`${isAssignedColumn ? 'bg-info bg-opacity-10' : ''} ${isAssignedColumn ? 'fw-bold' : ''} ${amountClass} ${alignClass}`}
                        >
                          {displayValue}
                        </td>
                      );
                    })}
                  </tr>
                )
              })}
            </tbody>
          </Table>
        </div>
      </Card.Body>
    </Card>
  );
};

export default ColumnMappingTable;
