import React, { useState } from 'react';
import Container from 'react-bootstrap/Container';
import Table from 'react-bootstrap/Table';
import Button from 'react-bootstrap/Button';
import Modal from 'react-bootstrap/Modal';
import Form from 'react-bootstrap/Form';
import { useSources, useCreateSource, useUpdateSource, useDeleteSource } from '../hooks/useQueries';
import { Source } from '../types';

const SourcesPage: React.FC = () => {
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [currentSource, setCurrentSource] = useState<Source | null>(null);
  const [sourceForm, setSourceForm] = useState({
    name: '',
    description: '',
  });

  const { data: sources, isLoading, isError } = useSources();
  const { mutate: createSource, isPending: isCreating } = useCreateSource();
  const { mutate: updateSource, isPending: isUpdating } = useUpdateSource();
  const { mutate: deleteSource, isPending: isDeleting } = useDeleteSource();

  const handleOpenCreateModal = () => {
    setSourceForm({ name: '', description: '' });
    setShowCreateModal(true);
  };

  const handleOpenEditModal = (source: Source) => {
    setCurrentSource(source);
    setSourceForm({
      name: source.name,
      description: source.description || '',
    });
    setShowEditModal(true);
  };

  const handleOpenDeleteModal = (source: Source) => {
    setCurrentSource(source);
    setShowDeleteModal(true);
  };

  const handleCloseModals = () => {
    setShowCreateModal(false);
    setShowEditModal(false);
    setShowDeleteModal(false);
    setCurrentSource(null);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setSourceForm(prev => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleCreateSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    createSource(
      {
        name: sourceForm.name,
        description: sourceForm.description || undefined,
      },
      {
        onSuccess: () => {
          handleCloseModals();
        },
      }
    );
  };

  const handleEditSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!currentSource) return;
    
    updateSource(
      {
        id: currentSource.id,
        source: {
          name: sourceForm.name,
          description: sourceForm.description || undefined,
        },
      },
      {
        onSuccess: () => {
          handleCloseModals();
        },
      }
    );
  };

  const handleDelete = () => {
    if (!currentSource) return;
    
    deleteSource(currentSource.id, {
      onSuccess: () => {
        handleCloseModals();
      },
    });
  };

  return (
    <Container>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1>Sources</h1>
        <Button variant="primary" onClick={handleOpenCreateModal}>
          Add New Source
        </Button>
      </div>

      {isLoading ? (
        <p>Loading sources...</p>
      ) : isError ? (
        <p>Error loading sources. Please try again.</p>
      ) : (
        <Table striped bordered hover responsive>
          <thead>
            <tr>
              <th>ID</th>
              <th>Name</th>
              <th>Description</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {sources && sources.length > 0 ? (
              sources.map(source => (
                <tr key={source.id}>
                  <td>{source.id}</td>
                  <td>{source.name}</td>
                  <td>{source.description || '-'}</td>
                  <td>
                    <Button 
                      variant="outline-primary" 
                      size="sm" 
                      className="me-2"
                      onClick={() => handleOpenEditModal(source)}
                      disabled={source.name === 'unknown'}
                    >
                      Edit
                    </Button>
                    <Button 
                      variant="outline-danger" 
                      size="sm"
                      onClick={() => handleOpenDeleteModal(source)}
                      disabled={source.name === 'unknown'}
                    >
                      Delete
                    </Button>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={4} className="text-center">No sources found</td>
              </tr>
            )}
          </tbody>
        </Table>
      )}

      {/* Create Modal */}
      <Modal show={showCreateModal} onHide={handleCloseModals}>
        <Modal.Header closeButton>
          <Modal.Title>Add New Source</Modal.Title>
        </Modal.Header>
        <Form onSubmit={handleCreateSubmit}>
          <Modal.Body>
            <Form.Group className="mb-3">
              <Form.Label>Source Name</Form.Label>
              <Form.Control
                type="text"
                name="name"
                value={sourceForm.name}
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
                value={sourceForm.description}
                onChange={handleInputChange}
              />
            </Form.Group>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={handleCloseModals}>
              Cancel
            </Button>
            <Button variant="primary" type="submit" disabled={isCreating}>
              {isCreating ? 'Adding...' : 'Add Source'}
            </Button>
          </Modal.Footer>
        </Form>
      </Modal>

      {/* Edit Modal */}
      <Modal show={showEditModal} onHide={handleCloseModals}>
        <Modal.Header closeButton>
          <Modal.Title>Edit Source</Modal.Title>
        </Modal.Header>
        <Form onSubmit={handleEditSubmit}>
          <Modal.Body>
            <Form.Group className="mb-3">
              <Form.Label>Source Name</Form.Label>
              <Form.Control
                type="text"
                name="name"
                value={sourceForm.name}
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
                value={sourceForm.description}
                onChange={handleInputChange}
              />
            </Form.Group>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={handleCloseModals}>
              Cancel
            </Button>
            <Button variant="primary" type="submit" disabled={isUpdating}>
              {isUpdating ? 'Saving...' : 'Save Changes'}
            </Button>
          </Modal.Footer>
        </Form>
      </Modal>

      {/* Delete Modal */}
      <Modal show={showDeleteModal} onHide={handleCloseModals}>
        <Modal.Header closeButton>
          <Modal.Title>Delete Source</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          Are you sure you want to delete the source "{currentSource?.name}"?
          This action cannot be undone.
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={handleCloseModals}>
            Cancel
          </Button>
          <Button variant="danger" onClick={handleDelete} disabled={isDeleting}>
            {isDeleting ? 'Deleting...' : 'Delete'}
          </Button>
        </Modal.Footer>
      </Modal>
    </Container>
  );
};

export default SourcesPage;
