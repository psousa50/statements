import React from 'react';
import { Container, Alert, Spinner } from 'react-bootstrap';
import { useSources } from '../../hooks/useQueries';
import type { Source } from '../../types';
import FileUploadZone from './FileUploadZone';
import AnalysisSummary from './AnalysisSummary';
import styles from './UploadPage.module.css';
import { UploadPageProvider } from './UploadPageContext';
import { useUploadPageContext } from './UploadPageContext';

const UploadPage: React.FC = () => {
  const { data: sources } = useSources();

  return (
    <UploadPageProvider>
      <Container className={styles.uploadPageContainer}>
        <UploadPageInner sources={sources} />
      </Container>
    </UploadPageProvider>
  );
};

const UploadPageInner: React.FC<{ sources: Source[] | undefined }> = ({ sources }) => {
  const {
    analysisResult,
    isAnalyzing,
    uploadResult,
    handleFileSelected,
  } = useUploadPageContext();

  return (
    <>
      {isAnalyzing && (
        <div style={{ display: 'flex', justifyContent: 'center', margin: '2rem 0' }}>
          <Spinner animation="border" role="status" aria-busy="true" data-testid="loading" style={{ width: 48, height: 48 }} />
        </div>
      )}
      {(!analysisResult && !isAnalyzing) && (
        <FileUploadZone onFileSelected={handleFileSelected} isLoading={isAnalyzing} />
      )}
      {analysisResult && (
        <AnalysisSummary sources={sources ?? []} />
      )}
      {uploadResult && !analysisResult && (
        <Alert variant={uploadResult.success ? 'success' : 'danger'} className="mb-4" role="alert">
          <Alert.Heading>{uploadResult.success ? 'Success!' : 'Error!'}</Alert.Heading>
          {uploadResult.message} Processed: {uploadResult.processed} Skipped: {uploadResult.skipped}
        </Alert>
      )}
    </>
  );
};

export default UploadPage;
