from src.app.schemas import ColumnMapping, StatementSchemaDefinition


def test_statement_schema_definition_fields():
    schema = StatementSchemaDefinition(
        id="test_id",
        file_type="CSV",
        column_mapping=ColumnMapping(
            date="Date",
            description="Description",
            amount="Amount",
            currency="EUR",
            balance="Balance"
        )
    )
    assert schema.id == "test_id"
    assert schema.file_type == "CSV"
    assert schema.column_mapping.date == "Date"
    assert schema.column_mapping.amount == "Amount"
