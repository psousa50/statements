import pytest
from unittest.mock import MagicMock, patch
import numpy as np
from src.app.services.categorizer import TransactionCategorizer
from src.app.models import Category


@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.fixture
def mock_categories():
    # Create mock categories for testing - use MagicMock instead of actual models
    main_category1 = MagicMock(spec=Category)
    main_category1.id = 1
    main_category1.category_name = "Food"
    main_category1.parent_category_id = None
    
    sub_category1 = MagicMock(spec=Category)
    sub_category1.id = 2
    sub_category1.category_name = "Restaurant"
    sub_category1.parent_category_id = 1
    
    sub_category2 = MagicMock(spec=Category)
    sub_category2.id = 3
    sub_category2.category_name = "Groceries"
    sub_category2.parent_category_id = 1
    
    main_category2 = MagicMock(spec=Category)
    main_category2.id = 4
    main_category2.category_name = "Transportation"
    main_category2.parent_category_id = None
    
    sub_category3 = MagicMock(spec=Category)
    sub_category3.id = 5
    sub_category3.category_name = "Taxi"
    sub_category3.parent_category_id = 4
    
    sub_category4 = MagicMock(spec=Category)
    sub_category4.id = 6
    sub_category4.category_name = "Public Transport"
    sub_category4.parent_category_id = 4
    
    # Set up relationships
    main_category1.subcategories = [sub_category1, sub_category2]
    main_category2.subcategories = [sub_category3, sub_category4]
    
    # For backward compatibility with the implementation
    main_category1.sub_categories = main_category1.subcategories
    main_category2.sub_categories = main_category2.subcategories
    
    return [main_category1, main_category2]


@pytest.fixture
def mock_model():
    # Create a mock model that returns embeddings
    mock_model = MagicMock()
    
    # Mock the encode method to return embeddings
    def mock_encode(texts):
        # Return a 2D array of embeddings, one for each text
        return np.array([
            [0.9, 0.1, 0.1, 0.1],  # Restaurant
            [0.1, 0.9, 0.1, 0.1],  # Groceries
            [0.1, 0.1, 0.9, 0.1],  # Taxi
            [0.1, 0.1, 0.1, 0.9],  # Public Transport
        ])
    
    mock_model.encode.side_effect = mock_encode
    
    return mock_model


@pytest.fixture
def mock_category_map():
    # Create a mapping from embedding index to (main_category_id, sub_category_id)
    return [
        (1, 2),  # Food -> Restaurant
        (1, 3),  # Food -> Groceries
        (4, 5),  # Transportation -> Taxi
        (4, 6),  # Transportation -> Public Transport
    ]


class TestTransactionCategorizer:
    def test_refresh_categories_embeddings(self, mock_categories, mock_model):
        # Create a mock categories repository
        mock_categories_repo = MagicMock()
        mock_categories_repo.get_all.return_value = mock_categories
        
        # Create a categorizer instance with the mocked repository and model
        categorizer = TransactionCategorizer(mock_categories_repo, model=mock_model)
        
        # Patch the encode method to return our expected embeddings
        with patch.object(mock_model, 'encode') as mock_encode:
            # Set up the mock to return the expected embeddings
            mock_encode.return_value = np.array([
                [0.9, 0.1, 0.1, 0.1],  # Restaurant
                [0.1, 0.9, 0.1, 0.1],  # Groceries
                [0.1, 0.1, 0.9, 0.1],  # Taxi
                [0.1, 0.1, 0.1, 0.9],  # Public Transport
            ])
            
            # Call the method we're testing
            (categories, category_map), embeddings = categorizer.refresh_categories_embeddings()
            
            # Verify that the categories were processed correctly
            assert categories == mock_categories
            assert len(category_map) == 4  # 4 subcategories
            assert category_map[0] == (1, 2)  # Food -> Restaurant
            assert category_map[1] == (1, 3)  # Food -> Groceries
            assert category_map[2] == (4, 5)  # Transportation -> Taxi
            assert category_map[3] == (4, 6)  # Transportation -> Public Transport
            
            # Verify that embeddings were generated
            assert embeddings.shape == (4, 4)  # 4 subcategories, 4-dimensional embeddings
    
    def test_categorize_transaction_restaurant(self, mock_categories, mock_model, mock_category_map):
        # Set up a mock similarity function that returns high similarity for restaurant
        def mock_similarity_restaurant(a, b):
            return np.array([0.9, 0.1, 0.1, 0.1])
        
        # Create a mock categories repository
        mock_categories_repo = MagicMock()
        mock_categories_repo.get_all.return_value = mock_categories
        
        # Create a categorizer instance with the mocked dependencies
        categorizer = TransactionCategorizer(mock_categories_repo, model=mock_model, similarity_func=mock_similarity_restaurant)
        
        # Set up the categorizer with our test data
        categorizer.categories = (mock_categories, mock_category_map)
        categorizer.embeddings = np.array([
            [0.9, 0.1, 0.1, 0.1],  # Restaurant
            [0.1, 0.9, 0.1, 0.1],  # Groceries
            [0.1, 0.1, 0.9, 0.1],  # Taxi
            [0.1, 0.1, 0.1, 0.9],  # Public Transport
        ])
        
        # Call the method we're testing
        category_id, confidence = categorizer.categorize_transaction("Dinner at a nice restaurant")
        
        # Verify that the transaction was categorized correctly
        assert category_id == 1  # Food (main category ID)
        assert confidence == 0.9
    
    def test_categorize_transaction_groceries(self, mock_categories, mock_model, mock_category_map):
        # Set up a mock similarity function that returns high similarity for groceries
        def mock_similarity_groceries(a, b):
            return np.array([0.1, 0.9, 0.1, 0.1])
        
        # Create a mock categories repository
        mock_categories_repo = MagicMock()
        mock_categories_repo.get_all.return_value = mock_categories
        
        # Create a categorizer instance with the mocked dependencies
        categorizer = TransactionCategorizer(mock_categories_repo, model=mock_model, similarity_func=mock_similarity_groceries)
        
        # Set up the categorizer with our test data
        categorizer.categories = (mock_categories, mock_category_map)
        categorizer.embeddings = np.array([
            [0.9, 0.1, 0.1, 0.1],  # Restaurant
            [0.1, 0.9, 0.1, 0.1],  # Groceries
            [0.1, 0.1, 0.9, 0.1],  # Taxi
            [0.1, 0.1, 0.1, 0.9],  # Public Transport
        ])
        
        # Call the method we're testing
        category_id, confidence = categorizer.categorize_transaction("Supermarket shopping")
        
        # Verify that the transaction was categorized correctly
        assert category_id == 1  # Food (main category ID)
        assert confidence == 0.9
    
    def test_categorize_transaction_taxi(self, mock_categories, mock_model, mock_category_map):
        # Set up a mock similarity function that returns high similarity for taxi
        def mock_similarity_taxi(a, b):
            return np.array([0.1, 0.1, 0.9, 0.1])
        
        # Create a mock categories repository
        mock_categories_repo = MagicMock()
        mock_categories_repo.get_all.return_value = mock_categories
        
        # Create a categorizer instance with the mocked dependencies
        categorizer = TransactionCategorizer(mock_categories_repo, model=mock_model, similarity_func=mock_similarity_taxi)
        
        # Set up the categorizer with our test data
        categorizer.categories = (mock_categories, mock_category_map)
        categorizer.embeddings = np.array([
            [0.9, 0.1, 0.1, 0.1],  # Restaurant
            [0.1, 0.9, 0.1, 0.1],  # Groceries
            [0.1, 0.1, 0.9, 0.1],  # Taxi
            [0.1, 0.1, 0.1, 0.9],  # Public Transport
        ])
        
        # Call the method we're testing
        category_id, confidence = categorizer.categorize_transaction("Taxi ride")
        
        # Verify that the transaction was categorized correctly
        assert category_id == 4  # Transportation (main category ID)
        assert confidence == 0.9
    
    def test_categorize_transaction_public_transport(self, mock_categories, mock_model, mock_category_map):
        # Set up a mock similarity function that returns high similarity for public transport
        def mock_similarity_public_transport(a, b):
            return np.array([0.1, 0.1, 0.1, 0.9])
        
        # Create a mock categories repository
        mock_categories_repo = MagicMock()
        mock_categories_repo.get_all.return_value = mock_categories
        
        # Create a categorizer instance with the mocked dependencies
        categorizer = TransactionCategorizer(mock_categories_repo, model=mock_model, similarity_func=mock_similarity_public_transport)
        
        # Set up the categorizer with our test data
        categorizer.categories = (mock_categories, mock_category_map)
        categorizer.embeddings = np.array([
            [0.9, 0.1, 0.1, 0.1],  # Restaurant
            [0.1, 0.9, 0.1, 0.1],  # Groceries
            [0.1, 0.1, 0.9, 0.1],  # Taxi
            [0.1, 0.1, 0.1, 0.9],  # Public Transport
        ])
        
        # Call the method we're testing
        category_id, confidence = categorizer.categorize_transaction("Bus ticket")
        
        # Verify that the transaction was categorized correctly
        assert category_id == 4  # Transportation (main category ID)
        assert confidence == 0.9
    
    def test_refresh_rules(self, mock_categories, mock_model, mock_category_map):
        # Create a mock categories repository
        mock_categories_repo = MagicMock()
        mock_categories_repo.get_all.return_value = mock_categories
        
        # Create a categorizer instance with the mocked dependencies
        categorizer = TransactionCategorizer(mock_categories_repo, model=mock_model)
        
        # Set up the categorizer with our test data
        categorizer.categories = (mock_categories, mock_category_map)
        categorizer.embeddings = np.array([
            [0.9, 0.1, 0.1, 0.1],  # Restaurant
            [0.1, 0.9, 0.1, 0.1],  # Groceries
            [0.1, 0.1, 0.9, 0.1],  # Taxi
            [0.1, 0.1, 0.1, 0.9],  # Public Transport
        ])
        
        # Patch the refresh_categories_embeddings method to return our test data
        with patch.object(categorizer, 'refresh_categories_embeddings') as mock_refresh:
            mock_refresh.return_value = ((mock_categories, mock_category_map), categorizer.embeddings)
            
            # Call the method we're testing
            categories, embeddings = categorizer.refresh_rules()
            
            # Verify that refresh_categories_embeddings was called
            mock_refresh.assert_called_once()
            
            # Verify that the rules were refreshed
            assert categories == (mock_categories, mock_category_map)
            assert np.array_equal(embeddings, categorizer.embeddings)
