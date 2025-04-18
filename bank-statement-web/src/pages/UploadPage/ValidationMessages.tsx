import { Alert } from 'react-bootstrap';

interface ValidationMessagesProps {
  columnMappings: Record<string, string>;
  isValid: boolean;
}

const ValidationMessages: React.FC<ValidationMessagesProps> = ({ columnMappings, isValid }) => {
  const hasDateColumn = Object.values(columnMappings).includes('date');
  const hasDescriptionColumn = Object.values(columnMappings).includes('description');
  const hasAmountColumn = Object.values(columnMappings).includes('amount');
  const hasDebitAmountColumn = Object.values(columnMappings).includes('debit_amount');
  const hasCreditAmountColumn = Object.values(columnMappings).includes('credit_amount');

  const bothDebitCreditAssigned = hasDebitAmountColumn && hasCreditAmountColumn;
  const onlyOneDebitCreditAssigned = (hasDebitAmountColumn || hasCreditAmountColumn) && !(hasDebitAmountColumn && hasCreditAmountColumn);
  const hasAmountAndDebitCredit = hasAmountColumn && (hasDebitAmountColumn || hasCreditAmountColumn);

  const amountRequired = !bothDebitCreditAssigned;

  const assignedTypes = Object.values(columnMappings).filter(
    v => v !== 'ignore' && v !== 'category'
  );
  const duplicates = assignedTypes.filter((v, i, arr) => arr.indexOf(v) !== i);
  const hasDuplicateAssignments = duplicates.length > 0;

  if (isValid) {
    return (
      <Alert variant="success" className="mb-4">
        <Alert.Heading>Ready to Upload</Alert.Heading>
        <p>Your column mappings look good! Click "Finalize Upload" to import your transactions.</p>
      </Alert>
    );
  }

  const hasIssues =
    !hasDateColumn ||
    !hasDescriptionColumn ||
    (amountRequired && !hasAmountColumn) ||
    onlyOneDebitCreditAssigned ||
    hasAmountAndDebitCredit ||
    hasDuplicateAssignments;

  return hasIssues ? (
    <Alert variant="warning" className="mb-4">
      <Alert.Heading>Please Fix the Following Issues:</Alert.Heading>
      <ul className="mb-0">
        {!hasDateColumn && (
          <li>Date column is required - please select which column contains transaction dates</li>
        )}
        {!hasDescriptionColumn && (
          <li>Description column is required - please select which column contains transaction descriptions</li>
        )}
        {amountRequired && !hasAmountColumn && (
          <li>Amount column is required unless both Debit and Credit columns are mapped</li>
        )}
        {onlyOneDebitCreditAssigned && (
          <li>If you assign either Debit or Credit column, you must assign both</li>
        )}
        {hasAmountAndDebitCredit && (
          <li>If using Debit and Credit columns, Amount column must not be assigned</li>
        )}
        {hasDuplicateAssignments && (
          <li>Each column type (except Ignore/Category) can only be assigned once</li>
        )}
      </ul>
    </Alert>
  ) : <div></div>;
};

export default ValidationMessages;
