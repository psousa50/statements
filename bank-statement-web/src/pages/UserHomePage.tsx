import React from 'react';
import { Link } from 'react-router-dom';
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Card from 'react-bootstrap/Card';
import Button from 'react-bootstrap/Button';
import Table from 'react-bootstrap/Table';
import { useTransactions, useCategories, useSources } from '../hooks/useQueries';
import { PieChart, Pie, Cell, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip } from 'recharts';
import './UserHomePage.css';

const UserHomePage: React.FC = () => {
  // Mock data - in a real app, this would come from API or context
  const userName = "John";
  const lastUpload = "5 days ago";
  
  const { data: transactions } = useTransactions({
    limit: 100, // Get enough transactions for calculations
    skip: 0,
  });
  
  const { data: categories } = useCategories();
  const { data: sources } = useSources();
  
  // Calculate metrics
  const metrics = React.useMemo(() => {
    if (!transactions) return {
      totalSpent: 0,
      autoCategorized: 0,
      mostCommonCategory: 'None',
      statementCount: 0
    };
    
    const currentMonth = new Date().getMonth();
    const currentYear = new Date().getFullYear();
    
    // Total spent this month (negative amounts)
    const totalSpent = transactions
      .filter(t => {
        const transDate = new Date(t.date);
        return transDate.getMonth() === currentMonth && 
               transDate.getFullYear() === currentYear && 
               t.amount < 0;
      })
      .reduce((sum, t) => sum + Math.abs(t.amount), 0);
    
    // Percentage of auto-categorized transactions
    const categorizedCount = transactions.filter(t => t.category_id !== null).length;
    const autoCategorized = transactions.length > 0 
      ? Math.round((categorizedCount / transactions.length) * 100) 
      : 0;
    
    // Most common category
    const categoryCounts: Record<string, number> = {};
    transactions.forEach(t => {
      if (t.category_id && categories) {
        const category = categories.find(c => c.id === t.category_id);
        if (category) {
          categoryCounts[category.category_name] = (categoryCounts[category.category_name] || 0) + 1;
        }
      }
    });
    
    let mostCommonCategory = 'None';
    let maxCount = 0;
    
    Object.entries(categoryCounts).forEach(([category, count]) => {
      if (count > maxCount) {
        mostCommonCategory = category;
        maxCount = count;
      }
    });
    
    // Count unique sources as a proxy for statement count
    const uniqueSources = new Set(transactions.map(t => t.source_id)).size;
    
    return {
      totalSpent,
      autoCategorized,
      mostCommonCategory,
      statementCount: uniqueSources
    };
  }, [transactions, categories]);
  
  // Prepare chart data
  const categoryChartData = React.useMemo(() => {
    if (!transactions || !categories) return [];
    
    const categoryAmounts: Record<string, number> = {};
    
    transactions.forEach(t => {
      if (t.category_id && t.amount < 0) { // Only count expenses
        const category = categories.find(c => c.id === t.category_id);
        if (category) {
          categoryAmounts[category.category_name] = (categoryAmounts[category.category_name] || 0) + Math.abs(t.amount);
        }
      }
    });
    
    return Object.entries(categoryAmounts)
      .map(([name, value]) => ({ name, value }))
      .sort((a, b) => b.value - a.value)
      .slice(0, 5); // Top 5 categories
  }, [transactions, categories]);
  
  // Merchant chart data
  const merchantChartData = React.useMemo(() => {
    if (!transactions) return [];
    
    const merchantAmounts: Record<string, number> = {};
    
    transactions.forEach(t => {
      if (t.amount < 0) { // Only count expenses
        // Use first word of description as merchant name (simplified)
        const merchant = t.description.split(' ')[0];
        merchantAmounts[merchant] = (merchantAmounts[merchant] || 0) + Math.abs(t.amount);
      }
    });
    
    return Object.entries(merchantAmounts)
      .map(([name, value]) => ({ name, value }))
      .sort((a, b) => b.value - a.value)
      .slice(0, 5); // Top 5 merchants
  }, [transactions]);
  
  // Mock recent activity data
  const recentActivity = [
    { id: 1, fileName: 'March_2025_Statement.pdf', uploadDate: '2025-04-05', transactionCount: 42, status: 'Processed' },
    { id: 2, fileName: 'Credit_Card_Q1.csv', uploadDate: '2025-03-15', transactionCount: 78, status: 'Processed' },
    { id: 3, fileName: 'Investment_Account.xls', uploadDate: '2025-02-28', transactionCount: 12, status: 'Processed' }
  ];
  
  // Format currency
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount);
  };
  
  // Chart colors
  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];
  
  return (
    <Container className="py-4">
      {/* Welcome Section */}
      <div className="mb-4">
        <h1 className="mb-2">Welcome back, {userName}!</h1>
        <p className="text-muted">Last upload: {lastUpload}</p>
      </div>
      
      <Row className="mb-4">
        {/* Quick Upload Widget */}
        <Col lg={4} className="mb-4">
          <Card className="h-100 shadow-sm">
            <Card.Body className="d-flex flex-column">
              <Card.Title>Quick Upload</Card.Title>
              <div 
                className="border border-dashed rounded p-4 text-center my-3 flex-grow-1 d-flex flex-column justify-content-center"
                style={{ borderStyle: 'dashed' }}
              >
                <div className="mb-3">
                  <i className="bi bi-cloud-upload fs-1 text-primary"></i>
                </div>
                <p>Drag & drop your statement file here</p>
                <p className="text-muted small">Supports PDF, CSV, XLS</p>
              </div>
              <Link to="/upload" className="mt-auto">
                <Button variant="primary" className="w-100">
                  Upload Statement
                </Button>
              </Link>
              <p className="text-muted small mt-2 mb-0">
                Your file will be analyzed and categorized automatically.
              </p>
            </Card.Body>
          </Card>
        </Col>
        
        {/* Key Metrics */}
        <Col lg={8}>
          <Row>
            <Col sm={6} md={3} className="mb-4">
              <Card className="h-100 shadow-sm">
                <Card.Body className="text-center">
                  <div className="mb-2">💸</div>
                  <div className="small text-muted">Total spent this month</div>
                  <div className="fs-4 fw-bold">{formatCurrency(metrics.totalSpent)}</div>
                </Card.Body>
              </Card>
            </Col>
            <Col sm={6} md={3} className="mb-4">
              <Card className="h-100 shadow-sm">
                <Card.Body className="text-center">
                  <div className="mb-2">🧠</div>
                  <div className="small text-muted">Auto-categorized</div>
                  <div className="fs-4 fw-bold">{metrics.autoCategorized}%</div>
                </Card.Body>
              </Card>
            </Col>
            <Col sm={6} md={3} className="mb-4">
              <Card className="h-100 shadow-sm">
                <Card.Body className="text-center">
                  <div className="mb-2">🏷️</div>
                  <div className="small text-muted">Most common category</div>
                  <div className="fs-4 fw-bold">{metrics.mostCommonCategory}</div>
                </Card.Body>
              </Card>
            </Col>
            <Col sm={6} md={3} className="mb-4">
              <Card className="h-100 shadow-sm">
                <Card.Body className="text-center">
                  <div className="mb-2">📄</div>
                  <div className="small text-muted">Uploaded statements</div>
                  <div className="fs-4 fw-bold">{metrics.statementCount}</div>
                </Card.Body>
              </Card>
            </Col>
          </Row>
        </Col>
      </Row>
      
      {/* Recent Activity */}
      <Row className="mb-4">
        <Col md={12}>
          <Card className="shadow-sm">
            <Card.Header className="bg-white">
              <div className="d-flex justify-content-between align-items-center">
                <h5 className="mb-0">Recent Activity</h5>
                <Link to="/upload">
                  <Button variant="outline-primary" size="sm">View All Statements</Button>
                </Link>
              </div>
            </Card.Header>
            <Card.Body>
              <Table responsive hover>
                <thead>
                  <tr>
                    <th>File Name</th>
                    <th>Upload Date</th>
                    <th>Transactions</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {recentActivity.map(activity => (
                    <tr key={activity.id}>
                      <td>{activity.fileName}</td>
                      <td>{new Date(activity.uploadDate).toLocaleDateString()}</td>
                      <td>{activity.transactionCount}</td>
                      <td>
                        <span className={`badge ${activity.status === 'Processed' ? 'bg-success' : 
                                              activity.status === 'In Progress' ? 'bg-warning' : 
                                              'bg-danger'}`}>
                          {activity.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </Table>
            </Card.Body>
          </Card>
        </Col>
      </Row>
      
      {/* Insights Preview */}
      <Row className="mb-4">
        <Col md={6} className="mb-4">
          <Card className="h-100 shadow-sm">
            <Card.Header className="bg-white">
              <h5 className="mb-0">Spending by Category</h5>
            </Card.Header>
            <Card.Body>
              {categoryChartData.length > 0 ? (
                <ResponsiveContainer width="100%" height={250}>
                  <PieChart>
                    <Pie
                      data={categoryChartData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                      label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                    >
                      {categoryChartData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value) => formatCurrency(Number(value))} />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <div className="text-center py-5 text-muted">
                  <p>No category data available</p>
                </div>
              )}
            </Card.Body>
          </Card>
        </Col>
        <Col md={6} className="mb-4">
          <Card className="h-100 shadow-sm">
            <Card.Header className="bg-white">
              <h5 className="mb-0">Top Merchants</h5>
            </Card.Header>
            <Card.Body>
              {merchantChartData.length > 0 ? (
                <ResponsiveContainer width="100%" height={250}>
                  <BarChart
                    data={merchantChartData}
                    layout="vertical"
                    margin={{ top: 5, right: 30, left: 80, bottom: 5 }}
                  >
                    <XAxis type="number" />
                    <YAxis type="category" dataKey="name" />
                    <Tooltip formatter={(value) => formatCurrency(Number(value))} />
                    <Bar dataKey="value" fill="#4f46e5" />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <div className="text-center py-5 text-muted">
                  <p>No merchant data available</p>
                </div>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default UserHomePage;
