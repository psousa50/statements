import React, { useState, useMemo } from 'react';
import Container from 'react-bootstrap/Container';
import Table from 'react-bootstrap/Table';
import Button from 'react-bootstrap/Button';
import Modal from 'react-bootstrap/Modal';
import Form from 'react-bootstrap/Form';
import { useCategories, useCreateCategory } from '../hooks/useQueries';
import { Category } from '../types';

const CategoriesPage: React.FC = () => {
  const [showModal, setShowModal] = useState(false);
  const [newCategory, setNewCategory] = useState({
    categoryName: '',
    parentCategoryId: null as number | null,
  });

  const { data: categories, isLoading, isError } = useCategories();
  const { mutate: createCategory, isPending: isCreating } = useCreateCategory();

  const handleOpenModal = () => setShowModal(true);
  const handleCloseModal = () => setShowModal(false);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setNewCategory(prev => ({
      ...prev,
      [name]: name === 'parentCategoryId' ? (value ? parseInt(value, 10) : null) : value,
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    createCategory(
      {
        categoryName: newCategory.categoryName,
        parentCategoryId: newCategory.parentCategoryId,
      },
      {
        onSuccess: () => {
          setNewCategory({
            categoryName: '',
            parentCategoryId: null,
          });
          handleCloseModal();
        },
      }
    );
  };

  // Organize categories into a hierarchy
  const { mainCategories, categoriesMap } = useMemo(() => {
    if (!categories) return { mainCategories: [], categoriesMap: new Map() };

    const map = new Map<number, Category>();
    const mains: Category[] = [];

    // First, populate the map
    categories.forEach(category => {
      map.set(category.id, category);
    });

    // Then, identify main categories (those without a parent)
    categories.forEach(category => {
      if (category.parentCategoryId === null) {
        mains.push(category);
      }
    });

    return { mainCategories: mains, categoriesMap: map };
  }, [categories]);

  // Render a category row with its subcategories
  const renderCategoryRow = (category: Category, level = 0) => {
    const indent = level * 20; // 20px indentation per level

    // Find subcategories
    const subcategories = categories?.filter(c => c.parentCategoryId === category.id) || [];

    return (
      <React.Fragment key={category.id}>
        <tr>
          <td>{category.id}</td>
          <td>
            <div style={{ paddingLeft: `${indent}px` }}>
              {category.categoryName}
            </div>
          </td>
          <td>
            {category.parentCategoryId
              ? categoriesMap.get(category.parentCategoryId)?.category_name || '-'
              : '-'}
          </td>
        </tr>
        {subcategories.map(subcat => renderCategoryRow(subcat, level + 1))}
      </React.Fragment>
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
              <th>Parent Category</th>
            </tr>
          </thead>
          <tbody>
            {mainCategories && mainCategories.length > 0 ? (
              mainCategories.map(category => renderCategoryRow(category))
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
                name="categoryName"
                value={newCategory.categoryName}
                onChange={handleInputChange}
                required
              />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Parent Category</Form.Label>
              <Form.Select
                name="parentCategoryId"
                value={newCategory.parentCategoryId?.toString() || ''}
                onChange={handleInputChange}
              >
                <option value="">None (Main Category)</option>
                {categories?.map(category => (
                  <option key={category.id} value={category.id}>
                    {category.categoryName}
                  </option>
                ))}
              </Form.Select>
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
