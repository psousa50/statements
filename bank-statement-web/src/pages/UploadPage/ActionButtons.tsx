import { Button } from 'react-bootstrap';

type Props = {
  onStartOver: () => void;
  onFinalize: () => void;
  isLoading: boolean;
  isValid: boolean;
};

export default function ActionButtons({ onStartOver, onFinalize, isLoading: isUploading, isValid }: Props) {
  return (
    <div className="d-flex justify-content-between mb-4">
      <Button
        variant="outline-secondary"
        onClick={onStartOver}
      >
        Start Over
      </Button>
      <div className="ms-auto">
        <Button
          variant="primary"
          onClick={onFinalize}
          disabled={!isValid || isUploading}
        >
          {isUploading ? 'Uploading...' : 'Finalize Upload'}
        </Button>
      </div>
    </div>
  );
}
