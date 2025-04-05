import React, { useState } from 'react';
import Button from 'react-bootstrap/Button';
import Form from 'react-bootstrap/Form';
import Card from 'react-bootstrap/Card';
import Alert from 'react-bootstrap/Alert';
import Container from 'react-bootstrap/Container';
import { useFileUpload, useSources } from '../hooks/useQueries';

const UploadPage: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [sourceId, setSourceId] = useState<number | undefined>(undefined);
  const [uploadResult, setUploadResult] = useState<{
    success: boolean;
    message: string;
    processed: number;
    skipped: number;
  } | null>(null);

  const { mutate: uploadFile, isPending } = useFileUpload();
  const { data: sources, isLoading: isLoadingSources } = useSources();

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
    }
  };

  const handleSourceChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value;
    const parsedValue = value ? parseInt(value) : undefined;
    console.log('Source selected:', value, 'Parsed value:', parsedValue);
    setSourceId(parsedValue);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!file) {
      return;
    }

    console.log('Submitting with sourceId:', sourceId);
    uploadFile(
      { file, sourceId },
      {
        onSuccess: (data) => {
          setUploadResult({
            success: true,
            message: data.message,
            processed: data.transactions_processed,
            skipped: data.skipped_duplicates,
          });
          setFile(null);
        },
        onError: (error) => {
          setUploadResult({
            success: false,
            message: error instanceof Error ? error.message : 'An error occurred during upload',
            processed: 0,
            skipped: 0,
          });
        },
      }
    );
  };

  return (
    <Container>
      <h1 className="mb-4">Upload Bank Statement</h1>
      
      <Card className="mb-4">
        <Card.Body>
          <Form onSubmit={handleSubmit}>
            <Form.Group className="mb-3">
              <Form.Label>Select File</Form.Label>
              <Form.Control 
                type="file" 
                onChange={handleFileChange}
                accept=".csv,.xls,.xlsx"
                required
              />
              <Form.Text className="text-muted">
                Supported formats: CSV, Excel (.xls, .xlsx)
              </Form.Text>
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Source</Form.Label>
              <Form.Select 
                value={sourceId || ''} 
                onChange={handleSourceChange} 
                disabled={isLoadingSources}
              >
                <option value="">Select a source (optional)</option>
                {sources?.map((source) => (
                  <option key={source.id} value={source.id}>
                    {source.name}
                  </option>
                ))}
              </Form.Select>
            </Form.Group>

            <Button 
              variant="primary" 
              type="submit" 
              disabled={!file || isPending}
            >
              {isPending ? 'Uploading...' : 'Upload'}
            </Button>
          </Form>
        </Card.Body>
      </Card>

      {uploadResult && (
        <Alert variant={uploadResult.success ? 'success' : 'danger'}>
          <Alert.Heading>{uploadResult.success ? 'Success!' : 'Error!'}</Alert.Heading>
          <p>{uploadResult.message}</p>
          {uploadResult.success && (
            <>
              <p>Transactions processed: {uploadResult.processed}</p>
              <p>Duplicate transactions skipped: {uploadResult.skipped}</p>
            </>
          )}
        </Alert>
      )}
    </Container>
  );
};

export default UploadPage;
