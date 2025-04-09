import React from 'react';
import { Link } from 'react-router-dom';
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Button from 'react-bootstrap/Button';
import Card from 'react-bootstrap/Card';
import Image from 'react-bootstrap/Image';
import './HomePage.css';

const HomePage: React.FC = () => {
  return (
    <>
      {/* Hero Section */}
      <section className="hero-section">
        <Container>
          <Row className="align-items-center">
            <Col lg={7} className="text-center text-lg-start mb-5 mb-lg-0">
              <h1 className="hero-title">Visualize Your Finances Effortlessly</h1>
              <p className="hero-subtitle">
                Upload your bank statements, let AI categorize and analyze your transactions for you.
              </p>
              <div className="hero-buttons">
                <Link to="/upload">
                  <Button variant="primary" size="lg" className="px-4 py-2">
                    Upload Statement
                  </Button>
                </Link>
                <Link to="/transactions">
                  <Button variant="outline-secondary" size="lg" className="px-4 py-2">
                    View Demo
                  </Button>
                </Link>
                <Link to="/user-home">
                  <Button variant="outline-primary" size="lg" className="px-4 py-2">
                    Login
                  </Button>
                </Link>
              </div>
            </Col>
            <Col lg={5}>
              <Image 
                src="https://placehold.co/600x400/e9ecef/6c757d?text=Dashboard+Preview" 
                alt="Dashboard Preview" 
                fluid 
                className="hero-image" 
              />
            </Col>
          </Row>
        </Container>
      </section>

      {/* Features Section */}
      <section className="features-section">
        <Container>
          <h2 className="section-title">Key Features</h2>
          <Row>
            <Col md={3} className="mb-4">
              <Card className="feature-card text-center">
                <Card.Body>
                  <div className="feature-icon">🤖</div>
                  <h3 className="feature-title">AI-Powered Categorization</h3>
                  <p className="feature-description">
                    Smart algorithms automatically categorize your transactions with high accuracy.
                  </p>
                </Card.Body>
              </Card>
            </Col>
            <Col md={3} className="mb-4">
              <Card className="feature-card text-center">
                <Card.Body>
                  <div className="feature-icon">📄</div>
                  <h3 className="feature-title">Multi-Format Support</h3>
                  <p className="feature-description">
                    Upload statements in PDF, CSV, or XLS formats with ease.
                  </p>
                </Card.Body>
              </Card>
            </Col>
            <Col md={3} className="mb-4">
              <Card className="feature-card text-center">
                <Card.Body>
                  <div className="feature-icon">📊</div>
                  <h3 className="feature-title">Interactive Dashboards</h3>
                  <p className="feature-description">
                    Visualize your spending patterns with beautiful, interactive charts.
                  </p>
                </Card.Body>
              </Card>
            </Col>
            <Col md={3} className="mb-4">
              <Card className="feature-card text-center">
                <Card.Body>
                  <div className="feature-icon">🔒</div>
                  <h3 className="feature-title">Secure & Private</h3>
                  <p className="feature-description">
                    Your financial data stays private and secure with our advanced protection.
                  </p>
                </Card.Body>
              </Card>
            </Col>
          </Row>
        </Container>
      </section>

      {/* How It Works Section */}
      <section className="how-it-works-section">
        <Container>
          <h2 className="section-title">How It Works</h2>
          <Row>
            <Col md={3} className="mb-4">
              <div className="step-card">
                <div className="step-number">1</div>
                <h3 className="step-title">Upload your statement</h3>
                <p className="step-description">
                  Simply drag and drop your bank statement file or select it from your device.
                </p>
              </div>
            </Col>
            <Col md={3} className="mb-4">
              <div className="step-card">
                <div className="step-number">2</div>
                <h3 className="step-title">Format is auto-detected</h3>
                <p className="step-description">
                  Our system automatically detects the format and maps the relevant columns.
                </p>
              </div>
            </Col>
            <Col md={3} className="mb-4">
              <div className="step-card">
                <div className="step-number">3</div>
                <h3 className="step-title">AI categorizes transactions</h3>
                <p className="step-description">
                  Transactions are intelligently categorized based on their descriptions.
                </p>
              </div>
            </Col>
            <Col md={3} className="mb-4">
              <div className="step-card">
                <div className="step-number">4</div>
                <h3 className="step-title">View trends and insights</h3>
                <p className="step-description">
                  Explore your spending habits through intuitive charts and detailed reports.
                </p>
              </div>
            </Col>
          </Row>
        </Container>
      </section>

      {/* Testimonial Section */}
      <section className="testimonial-section">
        <Container>
          <h2 className="section-title">What Our Users Say</h2>
          <Row>
            <Col md={4} className="mb-4">
              <Card className="testimonial-card">
                <Card.Body>
                  <p className="testimonial-text">
                    "This app saved me hours of spreadsheet work! The AI categorization is surprisingly accurate."
                  </p>
                  <p className="testimonial-author">— Sarah K., Financial Analyst</p>
                </Card.Body>
              </Card>
            </Col>
            <Col md={4} className="mb-4">
              <Card className="testimonial-card">
                <Card.Body>
                  <p className="testimonial-text">
                    "I finally understand where my money is going. The visualizations make it so clear and actionable."
                  </p>
                  <p className="testimonial-author">— Michael T., Small Business Owner</p>
                </Card.Body>
              </Card>
            </Col>
            <Col md={4} className="mb-4">
              <Card className="testimonial-card">
                <Card.Body>
                  <p className="testimonial-text">
                    "The multi-format support is fantastic. I can upload statements from all my different accounts."
                  </p>
                  <p className="testimonial-author">— Lisa R., Freelancer</p>
                </Card.Body>
              </Card>
            </Col>
          </Row>
        </Container>
      </section>

      {/* Footer */}
      <footer className="footer">
        <Container>
          <Row>
            <Col md={4} className="mb-4 mb-md-0">
              <div className="footer-logo">StatementApp</div>
              <p>Making financial management effortless through AI and smart visualization.</p>
            </Col>
            <Col md={4} className="mb-4 mb-md-0">
              <div className="footer-links">
                <Link to="/contact" className="footer-link">Contact</Link>
                <Link to="/privacy" className="footer-link">Privacy</Link>
                <Link to="/terms" className="footer-link">Terms</Link>
              </div>
            </Col>
            <Col md={4}>
              <div className="footer-social">
                <a href="https://twitter.com" className="social-icon" aria-label="Twitter"><i className="bi bi-twitter"></i></a>
                <a href="https://facebook.com" className="social-icon" aria-label="Facebook"><i className="bi bi-facebook"></i></a>
                <a href="https://linkedin.com" className="social-icon" aria-label="LinkedIn"><i className="bi bi-linkedin"></i></a>
                <a href="https://github.com" className="social-icon" aria-label="GitHub"><i className="bi bi-github"></i></a>
              </div>
              <p className="footer-copyright">&copy; 2025 StatementApp</p>
            </Col>
          </Row>
        </Container>
      </footer>
    </>
  );
};

export default HomePage;
