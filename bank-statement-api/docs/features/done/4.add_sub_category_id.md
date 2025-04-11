# Add sub_category_id to transaction

## Description

Add sub_category_id to transaction model and transaction create/update schemas.

The category_id is the main category of the transaction, while the sub_category_id is the subcategory of the transaction.
The category_id is always a main category, with parent_id = null
The sub_category_id is always a subcategory, with parent_category_id = some category_id

Make all necessary changes to the database and models.




