import React, { useState } from 'react';
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Card from 'react-bootstrap/Card';
import Form from 'react-bootstrap/Form';
import Button from 'react-bootstrap/Button';
import {
  PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import { useTransactions, useCategories, useSources } from '../hooks/useQueries';

// Colors for the charts
const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D', '#FFC658', '#8DD1E1'];

// Chart types for maximization
enum ChartType {
  NONE = 'none',
  CATEGORY = 'category',
  MONTHLY = 'monthly'
}

const ChartsPage: React.FC = () => {
  // State for filters
  const [startDate, setStartDate] = useState<string>('');
  const [endDate, setEndDate] = useState<string>('');
  const [categoryId, setCategoryId] = useState<number | undefined>(undefined);
  const [sourceId, setSourceId] = useState<number | undefined>(undefined);
  // State for maximized chart
  const [maximizedChart, setMaximizedChart] = useState<ChartType>(ChartType.NONE);

  // Fetch data
  const { data: transactions, isLoading: isLoadingTransactions } = useTransactions({
    startDate: startDate || undefined,
    endDate: endDate || undefined,
    categoryId: categoryId,
    sourceId: sourceId
  });
  const { data: categories, isLoading: isLoadingCategories } = useCategories();
  const { data: sources, isLoading: isLoadingSources } = useSources();

  // Prepare data for pie chart (by category)
  const prepareCategoryData = () => {
    if (!transactions || !categories) return [];

    const categoryMap = new Map<number, { name: string; value: number }>();

    // Initialize with all categories
    categories.forEach(category => {
      categoryMap.set(category.id, { name: category.categoryName, value: 0 });
    });

    // Sum transaction amounts by category
    transactions.forEach(transaction => {
      if (transaction.categoryId && transaction.amount < 0) { // Only count expenses (negative amounts)
        const categoryData = categoryMap.get(transaction.categoryId);
        if (categoryData) {
          categoryMap.set(
            transaction.categoryId,
            { ...categoryData, value: categoryData.value + Math.abs(transaction.amount) }
          );
        }
      }
    });

    // Convert to array and filter out categories with zero value
    return Array.from(categoryMap.values())
      .filter(item => item.value > 0)
      .sort((a, b) => b.value - a.value);
  };

  // Prepare data for bar chart (monthly expenses)
  const prepareMonthlyData = () => {
    if (!transactions) return [];

    const monthlyMap = new Map<string, { name: string; expenses: number; income: number }>();

    // Process transactions
    transactions.forEach(transaction => {
      const date = new Date(transaction.date);
      const monthYear = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
      const monthName = date.toLocaleString('default', { month: 'short', year: 'numeric' });

      if (!monthlyMap.has(monthYear)) {
        monthlyMap.set(monthYear, { name: monthName, expenses: 0, income: 0 });
      }

      const monthData = monthlyMap.get(monthYear)!;
      if (transaction.amount < 0) {
        monthlyMap.set(
          monthYear,
          { ...monthData, expenses: monthData.expenses + Math.abs(transaction.amount) }
        );
      } else {
        monthlyMap.set(
          monthYear,
          { ...monthData, income: monthData.income + transaction.amount }
        );
      }
    });

    // Convert to array and sort by date
    return Array.from(monthlyMap.values())
      .sort((a, b) => a.name.localeCompare(b.name));
  };

  const categoryData = prepareCategoryData();
  const monthlyData = prepareMonthlyData();

  const handleFilterChange = () => {
    // The filters are automatically applied through the useTransactions hook
  };

  const handleClearFilters = () => {
    setStartDate('');
    setEndDate('');
    setCategoryId(undefined);
    setSourceId(undefined);
  };

  // Toggle maximized state for a chart
  const toggleMaximize = (chartType: ChartType) => {
    setMaximizedChart(maximizedChart === chartType ? ChartType.NONE : chartType);
  };

  // Get column width based on maximized state
  const getColWidth = (chartType: ChartType) => {
    if (maximizedChart === ChartType.NONE) {
      return 6; // Default is half width (6 out of 12 columns)
    }
    return maximizedChart === chartType ? 12 : 0; // Full width if maximized, hidden if another chart is maximized
  };

  // Get chart height based on maximized state
  const getChartHeight = (chartType: ChartType) => {
    if (chartType === ChartType.CATEGORY) {
      return maximizedChart === chartType ? 700 : 400; // Increased height for pie chart
    }
    return maximizedChart === chartType ? 600 : 300; // Default for other charts
  };

  return (
    <Container>
      <h1 className="mb-4">Financial Charts</h1>

      {/* Filters */}
      <Card className="mb-4">
        <Card.Body>
          <h5>Filters</h5>
          <Row>
            <Col md={3}>
              <Form.Group className="mb-3">
                <Form.Label>Start Date</Form.Label>
                <Form.Control
                  type="date"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                />
              </Form.Group>
            </Col>
            <Col md={3}>
              <Form.Group className="mb-3">
                <Form.Label>End Date</Form.Label>
                <Form.Control
                  type="date"
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
                />
              </Form.Group>
            </Col>
            <Col md={3}>
              <Form.Group className="mb-3">
                <Form.Label>Category</Form.Label>
                <Form.Select
                  value={categoryId || ''}
                  onChange={(e) => setCategoryId(e.target.value ? parseInt(e.target.value) : undefined)}
                  disabled={isLoadingCategories}
                >
                  <option value="">All Categories</option>
                  {categories?.map((category) => (
                    <option key={category.id} value={category.id}>
                      {category.categoryName}
                    </option>
                  ))}
                </Form.Select>
              </Form.Group>
            </Col>
            <Col md={3}>
              <Form.Group className="mb-3">
                <Form.Label>Source</Form.Label>
                <Form.Select
                  value={sourceId || ''}
                  onChange={(e) => setSourceId(e.target.value ? parseInt(e.target.value) : undefined)}
                  disabled={isLoadingSources}
                >
                  <option value="">All Sources</option>
                  {sources?.map((source) => (
                    <option key={source.id} value={source.id}>
                      {source.name}
                    </option>
                  ))}
                </Form.Select>
              </Form.Group>
            </Col>
          </Row>
          <div className="d-flex justify-content-end">
            <Button variant="secondary" onClick={handleClearFilters} className="me-2">
              Clear Filters
            </Button>
            <Button variant="primary" onClick={handleFilterChange}>
              Apply Filters
            </Button>
          </div>
        </Card.Body>
      </Card>

      {/* Charts */}
      <Row>
        {/* Pie Chart - Expenses by Category */}
        {(maximizedChart === ChartType.NONE || maximizedChart === ChartType.CATEGORY) && (
          <Col md={getColWidth(ChartType.CATEGORY)}>
            <Card className="mb-4">
              <Card.Body>
                <div className="d-flex justify-content-between align-items-center mb-3">
                  <h5>Expenses by Category</h5>
                  <Button
                    variant="outline-secondary"
                    size="sm"
                    onClick={() => toggleMaximize(ChartType.CATEGORY)}
                  >
                    {maximizedChart === ChartType.CATEGORY ? 'Minimize' : 'Maximize'}
                  </Button>
                </div>
                {isLoadingTransactions || isLoadingCategories ? (
                  <div className="text-center p-5">Loading...</div>
                ) : categoryData.length > 0 ? (
                  <ResponsiveContainer width="100%" height={getChartHeight(ChartType.CATEGORY)}>
                    <PieChart>
                      <Pie
                        data={categoryData}
                        cx="50%"
                        cy="50%"
                        labelLine={true}
                        label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                        outerRadius={maximizedChart === ChartType.CATEGORY ? 200 : 120}
                        fill="#8884d8"
                        dataKey="value"
                      >
                        {categoryData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip
                        formatter={(value: number) => [`€${value.toFixed(2)}`, 'Amount']}
                      />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="text-center p-5">No data available</div>
                )}
              </Card.Body>
            </Card>
          </Col>
        )}

        {/* Bar Chart - Monthly Income/Expenses */}
        {(maximizedChart === ChartType.NONE || maximizedChart === ChartType.MONTHLY) && (
          <Col md={getColWidth(ChartType.MONTHLY)}>
            <Card className="mb-4">
              <Card.Body>
                <div className="d-flex justify-content-between align-items-center mb-3">
                  <h5>Monthly Income & Expenses</h5>
                  <Button
                    variant="outline-secondary"
                    size="sm"
                    onClick={() => toggleMaximize(ChartType.MONTHLY)}
                  >
                    {maximizedChart === ChartType.MONTHLY ? 'Minimize' : 'Maximize'}
                  </Button>
                </div>
                {isLoadingTransactions ? (
                  <div className="text-center p-5">Loading...</div>
                ) : monthlyData.length > 0 ? (
                  <ResponsiveContainer width="100%" height={getChartHeight(ChartType.MONTHLY)}>
                    <BarChart
                      data={monthlyData}
                      margin={{
                        top: 20,
                        right: 30,
                        left: 20,
                        bottom: 5,
                      }}
                    >
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" />
                      <YAxis />
                      <Tooltip formatter={(value: number) => [`€${value.toFixed(2)}`, '']} />
                      <Legend />
                      <Bar dataKey="income" name="Income" fill="#82ca9d" />
                      <Bar dataKey="expenses" name="Expenses" fill="#8884d8" />
                    </BarChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="text-center p-5">No data available</div>
                )}
              </Card.Body>
            </Card>
          </Col>
        )}
      </Row>

      {/* Summary Statistics - Only show when no chart is maximized */}
      {maximizedChart === ChartType.NONE && (
        <Row>
          <Col>
            <Card className="mb-4">
              <Card.Body>
                <h5>Summary Statistics</h5>
                {isLoadingTransactions ? (
                  <div className="text-center p-3">Loading...</div>
                ) : transactions ? (
                  <Row>
                    <Col md={3}>
                      <div className="text-center">
                        <h6>Total Income</h6>
                        <h4 className="text-success">
                          €{transactions
                            .filter(t => t.amount > 0)
                            .reduce((sum, t) => sum + t.amount, 0)
                            .toFixed(2)}
                        </h4>
                      </div>
                    </Col>
                    <Col md={3}>
                      <div className="text-center">
                        <h6>Total Expenses</h6>
                        <h4 className="text-danger">
                          €{Math.abs(transactions
                            .filter(t => t.amount < 0)
                            .reduce((sum, t) => sum + t.amount, 0))
                            .toFixed(2)}
                        </h4>
                      </div>
                    </Col>
                    <Col md={3}>
                      <div className="text-center">
                        <h6>Balance</h6>
                        <h4 className={transactions.reduce((sum, t) => sum + t.amount, 0) >= 0 ? 'text-success' : 'text-danger'}>
                          €{transactions
                            .reduce((sum, t) => sum + t.amount, 0)
                            .toFixed(2)}
                        </h4>
                      </div>
                    </Col>
                    <Col md={3}>
                      <div className="text-center">
                        <h6>Transaction Count</h6>
                        <h4>{transactions.length}</h4>
                      </div>
                    </Col>
                  </Row>
                ) : (
                  <div className="text-center p-3">No data available</div>
                )}
              </Card.Body>
            </Card>
          </Col>
        </Row>
      )}
    </Container>
  );
};

export default ChartsPage;
