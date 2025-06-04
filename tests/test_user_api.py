import unittest
import tempfile
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import json
import jwt
import datetime

class TestUserAPI(unittest.TestCase):
    def setUp(self):
        # Create a temporary database file
        self.db_fd, self.db_path = tempfile.mkstemp()
        os.environ['DATABASE_URL'] = f'sqlite:///{self.db_path}'
        from src.fit.database import reload_engine_and_session
        reload_engine_and_session()
        from src.fit.app import create_app
        from src.fit.database import init_db, db_session, Base
        from src.fit.models_db import UserModel
        self.app = create_app({
            'TESTING': True,
            'DATABASE_URL': f'sqlite:///{self.db_path}',
            'SECRET_KEY': 'test-secret-key'
        })
        self.client = self.app.test_client()
        
        # Set up test database with SQLite engine
        test_engine = create_engine(f'sqlite:///{self.db_path}')
        TestSession = sessionmaker(bind=test_engine)
        self.db = TestSession()
        
        # Create tables
        Base.metadata.create_all(bind=test_engine)
        
        # Create a mock admin token
        token_data = {
            "sub": "admin@test.com",
            "name": "Test Admin",
            "role": "admin",
            "iss": "fit-api",
            "iat": datetime.datetime.now(datetime.UTC),
            "exp": datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=30)
        }
        self.admin_token = jwt.encode(token_data, "fit-secret-key", algorithm="HS256")
        
        # Import services here to avoid circular imports
        from src.fit.services.user_service import create_user as create_user_service
        from src.fit.services.user_service import get_all_users as get_all_users_service
        from src.fit.services.user_service import update_user_profile, get_user_profile
        from src.fit.services.auth_service import admin_required, jwt_required
        
    def tearDown(self):
        # Clean up the database after each test
        self.db.close()
        os.close(self.db_fd)
        os.unlink(self.db_path)
        
    def test_create_user_success(self):
        # Test data
        test_user = {
            "email": "test@example.com",
            "name": "Test User",
            "role": "user"
        }
        
        # Make the request with admin token
        response = self.client.post(
            '/users',
            data=json.dumps(test_user),
            content_type='application/json',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        # Assert response
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['email'], test_user['email'])
        self.assertEqual(data['name'], test_user['name'])
        self.assertEqual(data['role'], test_user['role'])
        self.assertIn('password', data)  # Should include generated password
        
    def test_create_user_invalid_data(self):
        # Test with invalid data (missing required fields)
        invalid_user = {
            "email": "invalid_email_format",  # Invalid email format
            "name": "Test User"
            # Missing role field
        }
        
        # Make the request with admin token
        response = self.client.post(
            '/users',
            data=json.dumps(invalid_user),
            content_type='application/json',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        # Assert response - should be 400 for invalid data
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)

if __name__ == '__main__':
    unittest.main()