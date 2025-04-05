import React, { useState } from 'react';
import Container from 'react-bootstrap/Container';
import Table from 'react-bootstrap/Table';
import Button from 'react-bootstrap/Button';
import Modal from 'react-bootstrap/Modal';
import Form from 'react-bootstrap/Form';
import { useCategories, useCreateCategory } from '../hooks/useQueries';

const CategoriesPage: React.FC = () => {
  const [showModal, setShowModal] = useState(false);
  const [newCategory, setNewCategory] = useState({
    category_name: '',
    description: '',
  });

  const { data: categories, isLoading, isError } = useCategories();
  const { mutate: createCategory, isPending: isCreating } = useCreateCategory();

  const handleOpenModal = () => setShowModal(true);
  const handleCloseModal = () => setShowModal(false);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setNewCategory(prev => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    createCategory(
      {
        category_name: newCategory.category_name,
        description: newCategory.description || undefined,
      },
      {
        onSuccess: () => {
          setNewCategory({
            category_name: '',
            description: '',
          });
          handleCloseModal();
        },
      }
    );
  };

  return (
    <Container>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1>Categories</h1>
        <Button variant="primary" onClick={handleOpenModal}>
          Add New Category
        </Button>
      </div>

      {isLoading ? (
        <p>Loading categories...</p>
      ) : isError ? (
        <p>Error loading categories. Please try again.</p>
      ) : (
        <Table striped bordered hover responsive>
          <thead>
            <tr>
              <th>ID</th>
              <th>Name</th>
              <th>Description</th>
            </tr>
          </thead>
          <tbody>
            {categories && categories.length > 0 ? (
              categories.map(category => (
                <tr key={category.id}>
                  <td>{category.id}</td>
                  <td>{category.category_name}</td>
                  <td>{category.description || '-'}</td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={3} className="text-center">No categories found</td>
              </tr>
            )}
          </tbody>
        </Table>
      )}

      <Modal show={showModal} onHide={handleCloseModal}>
        <Modal.Header closeButton>
          <Modal.Title>Add New Category</Modal.Title>
        </Modal.Header>
        <Form onSubmit={handleSubmit}>
          <Modal.Body>
            <Form.Group className="mb-3">
              <Form.Label>Category Name</Form.Label>
              <Form.Control
                type="text"
                name="category_name"
                value={newCategory.category_name}
                onChange={handleInputChange}
                required
              />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Description</Form.Label>
              <Form.Control
                as="textarea"
                rows={3}
                name="description"
                value={newCategory.description}
                onChange={handleInputChange}
              />
            </Form.Group>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={handleCloseModal}>
              Cancel
            </Button>
            <Button variant="primary" type="submit" disabled={isCreating}>
              {isCreating ? 'Adding...' : 'Add Category'}
            </Button>
          </Modal.Footer>
        </Form>
      </Modal>
    </Container>
  );
};

export default CategoriesPage;
