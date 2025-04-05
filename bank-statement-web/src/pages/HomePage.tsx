import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Card from 'react-bootstrap/Card';
import Button from 'react-bootstrap/Button';
import Table from 'react-bootstrap/Table';
import Form from 'react-bootstrap/Form';
import InputGroup from 'react-bootstrap/InputGroup';
import Badge from 'react-bootstrap/Badge';
import { useTransactions, useCategories, useSources } from '../hooks/useQueries';
import { Transaction } from '../types';
import './HomePage.css';

const HomePage: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  
  // Fetch the most recent transactions (limited to 5)
  const { data: recentTransactions, isLoading } = useTransactions({
    limit: 5,
    skip: 0,
  });
  
  const { data: categories } = useCategories();
  const { data: sources } = useSources();

  // Calculate total income and expenses from recent transactions
  const financialSummary = React.useMemo(() => {
    if (!recentTransactions) return { income: 0, expenses: 0, balance: 0 };
    
    const income = recentTransactions
      .filter(t => t.amount > 0)
      .reduce((sum, t) => sum + t.amount, 0);
      
    const expenses = recentTransactions
      .filter(t => t.amount < 0)
      .reduce((sum, t) => sum + Math.abs(t.amount), 0);
      
    return {
      income,
      expenses,
      balance: income - expenses
    };
  }, [recentTransactions]);

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString();
  };

  const formatAmount = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount);
  };

  const getCategoryName = (categoryId: number | null) => {
    if (!categoryId || !categories) return 'Uncategorized';
    const category = categories.find(c => c.id === categoryId);
    return category ? category.category_name : 'Uncategorized';
  };

  const getSourceName = (sourceId: number) => {
    if (!sources) return 'Unknown';
    const source = sources.find(s => s.id === sourceId);
    return source ? source.name : 'Unknown';
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    // Navigate to transactions page with search term
    window.location.href = `/transactions?search=${encodeURIComponent(searchTerm)}`;
  };

  return (
    <Container>
      <div className="home-header text-center mb-5 p-4">
        <h1 className="display-4 mb-3">Bank Statement Manager</h1>
        <p className="lead">Manage, analyze, and categorize your financial transactions in one place</p>
        
        <Form onSubmit={handleSearch} className="mt-4 mb-3 search-container">
          <InputGroup>
            <Form.Control
              type="text"
              placeholder="Search transactions..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="search-input"
            />
            <Button variant="primary" type="submit" className="search-button">
              Search
            </Button>
          </InputGroup>
        </Form>
      </div>

      <Row className="mb-4">
        <Col md={4}>
          <Card className="h-100 shadow-sm stat-card income-card">
            <Card.Body className="text-center">
              <div className="summary-icon text-success">
                <i className="bi bi-arrow-down-circle"></i>
              </div>
              <Card.Title>Income</Card.Title>
              <h3 className="summary-value text-success">{formatAmount(financialSummary.income)}</h3>
              <Card.Text className="summary-label">Recent incoming transactions</Card.Text>
            </Card.Body>
          </Card>
        </Col>
        <Col md={4}>
          <Card className="h-100 shadow-sm stat-card expense-card">
            <Card.Body className="text-center">
              <div className="summary-icon text-danger">
                <i className="bi bi-arrow-up-circle"></i>
              </div>
              <Card.Title>Expenses</Card.Title>
              <h3 className="summary-value text-danger">{formatAmount(financialSummary.expenses)}</h3>
              <Card.Text className="summary-label">Recent outgoing transactions</Card.Text>
            </Card.Body>
          </Card>
        </Col>
        <Col md={4}>
          <Card className="h-100 shadow-sm stat-card balance-card">
            <Card.Body className="text-center">
              <div className="summary-icon text-info">
                <i className="bi bi-wallet2"></i>
              </div>
              <Card.Title>Balance</Card.Title>
              <h3 className={`summary-value ${financialSummary.balance >= 0 ? "text-success" : "text-danger"}`}>
                {formatAmount(financialSummary.balance)}
              </h3>
              <Card.Text className="summary-label">Net balance from recent transactions</Card.Text>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      <Row className="mb-5">
        <Col md={8}>
          <Card className="shadow-sm">
            <Card.Header className="d-flex justify-content-between align-items-center bg-white">
              <h5 className="mb-0">Recent Transactions</h5>
              <Link to="/transactions">
                <Button variant="outline-primary" size="sm">View All</Button>
              </Link>
            </Card.Header>
            <Card.Body>
              {isLoading ? (
                <p className="text-center">Loading transactions...</p>
              ) : !recentTransactions || recentTransactions.length === 0 ? (
                <div className="text-center py-4">
                  <p>No transactions found</p>
                  <Link to="/upload">
                    <Button variant="primary" className="action-button">Upload Transactions</Button>
                  </Link>
                </div>
              ) : (
                <Table hover responsive className="mb-0">
                  <thead>
                    <tr>
                      <th>Date</th>
                      <th>Description</th>
                      <th>Category</th>
                      <th>Amount</th>
                    </tr>
                  </thead>
                  <tbody>
                    {recentTransactions.map((transaction: Transaction) => (
                      <tr key={transaction.id} className="transaction-row">
                        <td>{formatDate(transaction.date)}</td>
                        <td className="text-truncate" style={{ maxWidth: '200px' }}>
                          {transaction.description}
                        </td>
                        <td>
                          <Badge bg="secondary" pill className="category-badge">
                            {getCategoryName(transaction.category_id)}
                          </Badge>
                        </td>
                        <td className={transaction.amount >= 0 ? "text-success" : "text-danger"}>
                          {formatAmount(transaction.amount)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              )}
            </Card.Body>
          </Card>
        </Col>
        <Col md={4}>
          <Card className="shadow-sm mb-4 quick-action-card">
            <Card.Header className="bg-white">
              <h5 className="mb-0">Quick Actions</h5>
            </Card.Header>
            <Card.Body>
              <div className="d-grid gap-2">
                <Link to="/upload">
                  <Button variant="primary" className="w-100 mb-2 action-button">
                    <i className="bi bi-upload me-2"></i>Upload Statements
                  </Button>
                </Link>
                <Link to="/transactions">
                  <Button variant="outline-secondary" className="w-100 mb-2 action-button">
                    <i className="bi bi-list-ul me-2"></i>View All Transactions
                  </Button>
                </Link>
                <Link to="/categories">
                  <Button variant="outline-secondary" className="w-100 mb-2 action-button">
                    <i className="bi bi-tag me-2"></i>Manage Categories
                  </Button>
                </Link>
                <Link to="/charts">
                  <Button variant="outline-secondary" className="w-100 action-button">
                    <i className="bi bi-bar-chart me-2"></i>View Analytics
                  </Button>
                </Link>
              </div>
            </Card.Body>
          </Card>
          
          <Card className="shadow-sm">
            <Card.Header className="bg-white">
              <h5 className="mb-0">Sources</h5>
            </Card.Header>
            <Card.Body>
              {!sources || sources.length === 0 ? (
                <p className="text-center">No sources found</p>
              ) : (
                <div className="d-flex flex-wrap">
                  {sources.slice(0, 5).map(source => (
                    <Badge 
                      key={source.id} 
                      bg="info" 
                      className="source-badge"
                    >
                      {source.name}
                    </Badge>
                  ))}
                  {sources.length > 5 && (
                    <Link to="/sources">
                      <Badge bg="secondary" className="source-badge">
                        +{sources.length - 5} more
                      </Badge>
                    </Link>
                  )}
                </div>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default HomePage;
