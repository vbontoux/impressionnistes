"""
Simple test to verify Lambda function imports work correctly
"""
import sys
import os

# Add parent directory to path for shared imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_imports():
    """Test that all auth Lambda functions can be imported"""
    print("Testing Lambda function imports...")
    
    try:
        # Test register
        from register import lambda_handler as register_handler
        print("✓ register.py imports successfully")
        
        # Test get_profile
        from get_profile import lambda_handler as get_profile_handler
        print("✓ get_profile.py imports successfully")
        
        # Test update_profile
        from update_profile import lambda_handler as update_profile_handler
        print("✓ update_profile.py imports successfully")
        
        # Test forgot_password
        from forgot_password import lambda_handler as forgot_password_handler
        print("✓ forgot_password.py imports successfully")
        
        # Test confirm_password_reset
        from confirm_password_reset import lambda_handler as confirm_password_reset_handler
        print("✓ confirm_password_reset.py imports successfully")
        
        print("\n✓ All Lambda functions import successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Import failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
