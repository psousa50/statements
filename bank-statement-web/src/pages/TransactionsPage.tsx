import React, { useState } from 'react';
import Container from 'react-bootstrap/Container';
import Table from 'react-bootstrap/Table';
import Form from 'react-bootstrap/Form';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Card from 'react-bootstrap/Card';
import Pagination from 'react-bootstrap/Pagination';
import { useTransactions, useCategories, useSources } from '../hooks/useQueries';
import { Transaction } from '../types';
import { TransactionCategoryEditor } from '../components/TransactionCategoryEditor';

const TransactionsPage: React.FC = () => {
  const [filters, setFilters] = useState({
    start_date: '',
    end_date: '',
    category_id: '',
    source_id: '',
    search: '',
    skip: 0,
    limit: 20,
  });

  const { data: transactions, isLoading, isError } = useTransactions(
    {
      start_date: filters.start_date || undefined,
      end_date: filters.end_date || undefined,
      category_id: filters.category_id ? parseInt(filters.category_id) : undefined,
      source_id: filters.source_id ? parseInt(filters.source_id) : undefined,
      search: filters.search || undefined,
      skip: filters.skip,
      limit: filters.limit,
    }
  );

  const { data: categories } = useCategories();
  const { data: sources } = useSources();

  const handleFilterChange = (e: any) => {
    const { name, value } = e.target;
    setFilters(prev => ({
      ...prev,
      [name]: value,
      skip: 0, // Reset pagination when filters change
    }));
  };

  const handlePageChange = (newSkip: number) => {
    setFilters(prev => ({
      ...prev,
      skip: newSkip,
    }));
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString();
  };

  const formatAmount = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD', // Default to USD if currency not provided
    }).format(amount);
  };

  const getSourceName = (sourceId: number) => {
    if (!sources) return 'Unknown';
    const source = sources.find(s => s.id === sourceId);
    return source ? source.name : 'Unknown';
  };

  const renderPagination = () => {
    if (!transactions || transactions.length === 0) return null;

    const currentPage = Math.floor(filters.skip / filters.limit) + 1;
    const hasMore = transactions.length === filters.limit;

    return (
      <Pagination className="mt-3 justify-content-center">
        <Pagination.Prev 
          onClick={() => handlePageChange(Math.max(0, filters.skip - filters.limit))}
          disabled={filters.skip === 0}
        />
        <Pagination.Item active>{currentPage}</Pagination.Item>
        <Pagination.Next 
          onClick={() => handlePageChange(filters.skip + filters.limit)}
          disabled={!hasMore}
        />
      </Pagination>
    );
  };

  return (
    <Container>
      <h1 className="mb-4">Transactions</h1>

      <Card className="mb-4">
        <Card.Body>
          <Row>
            <Col md={3}>
              <Form.Group className="mb-3">
                <Form.Label>Start Date</Form.Label>
                <Form.Control
                  type="date"
                  name="start_date"
                  value={filters.start_date}
                  onChange={handleFilterChange}
                />
              </Form.Group>
            </Col>
            <Col md={3}>
              <Form.Group className="mb-3">
                <Form.Label>End Date</Form.Label>
                <Form.Control
                  type="date"
                  name="end_date"
                  value={filters.end_date}
                  onChange={handleFilterChange}
                />
              </Form.Group>
            </Col>
            <Col md={3}>
              <Form.Group className="mb-3">
                <Form.Label>Category</Form.Label>
                <Form.Select 
                  name="category_id"
                  value={filters.category_id}
                  onChange={handleFilterChange}
                >
                  <option value="">All Categories</option>
                  {categories?.map(category => (
                    <option key={category.id} value={category.id}>
                      {category.category_name}
                    </option>
                  ))}
                </Form.Select>
              </Form.Group>
            </Col>
            <Col md={3}>
              <Form.Group className="mb-3">
                <Form.Label>Source</Form.Label>
                <Form.Select 
                  name="source_id"
                  value={filters.source_id}
                  onChange={handleFilterChange}
                >
                  <option value="">All Sources</option>
                  {sources?.map(source => (
                    <option key={source.id} value={source.id}>
                      {source.name}
                    </option>
                  ))}
                </Form.Select>
              </Form.Group>
            </Col>
          </Row>
          <Row>
            <Col>
              <Form.Group className="mb-3">
                <Form.Label>Search</Form.Label>
                <Form.Control
                  type="text"
                  name="search"
                  value={filters.search}
                  onChange={handleFilterChange}
                  placeholder="Search by description"
                />
              </Form.Group>
            </Col>
          </Row>
        </Card.Body>
      </Card>

      {isLoading ? (
        <p>Loading transactions...</p>
      ) : isError ? (
        <p>Error loading transactions. Please try again.</p>
      ) : (
        <>
          <Table striped bordered hover responsive>
            <thead>
              <tr>
                <th>Date</th>
                <th>Description</th>
                <th>Amount</th>
                <th>Category</th>
                <th>Source</th>
              </tr>
            </thead>
            <tbody>
              {transactions && transactions.length > 0 ? (
                transactions.map((transaction: Transaction) => (
                  <tr key={transaction.id}>
                    <td>{formatDate(transaction.date)}</td>
                    <td>{transaction.description}</td>
                    <td className={transaction.amount < 0 ? 'text-danger' : 'text-success'}>
                      {formatAmount(transaction.amount)}
                    </td>
                    <td>
                      <TransactionCategoryEditor 
                        transaction={transaction} 
                      />
                    </td>
                    <td>{getSourceName(transaction.source_id)}</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={5} className="text-center">No transactions found</td>
                </tr>
              )}
            </tbody>
          </Table>
          {renderPagination()}
        </>
      )}
    </Container>
  );
};

export default TransactionsPage;
