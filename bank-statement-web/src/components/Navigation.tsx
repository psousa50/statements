import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import Navbar from 'react-bootstrap/Navbar';
import Nav from 'react-bootstrap/Nav';
import Container from 'react-bootstrap/Container';
import NavDropdown from 'react-bootstrap/NavDropdown';

const Navigation: React.FC = () => {
  const location = useLocation();
  
  return (
    <Navbar bg="white" expand="lg" className="mb-4 fixed-top shadow-sm">
      <Container>
        <Navbar.Brand as={Link} to="/" className="fw-bold">StatementApp</Navbar.Brand>
        <Navbar.Toggle aria-controls="basic-navbar-nav" />
        <Navbar.Collapse id="basic-navbar-nav">
          <Nav className="ms-auto">
            <Nav.Link 
              as={Link} 
              to="/" 
              active={location.pathname === '/'}
            >
              Home
            </Nav.Link>
            <Nav.Link 
              as={Link} 
              to="/upload" 
              active={location.pathname === '/upload'}
            >
              Upload
            </Nav.Link>
            <Nav.Link 
              as={Link} 
              to="/transactions" 
              active={location.pathname.startsWith('/transactions')}
            >
              Dashboard
            </Nav.Link>
            <Nav.Link 
              as={Link} 
              to="/about" 
              active={location.pathname === '/about'}
            >
              About
            </Nav.Link>
            <NavDropdown title="Account" id="account-dropdown">
              <NavDropdown.Item as={Link} to="/profile">Profile</NavDropdown.Item>
              <NavDropdown.Item as={Link} to="/settings">Settings</NavDropdown.Item>
              <NavDropdown.Divider />
              <NavDropdown.Item as={Link} to="/logout">Logout</NavDropdown.Item>
            </NavDropdown>
          </Nav>
        </Navbar.Collapse>
      </Container>
    </Navbar>
  );
};

export default Navigation;
