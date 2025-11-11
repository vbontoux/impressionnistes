# Backend - Course des Impressionnistes Registration System

Python backend with Lambda functions and shared utilities.

## Structure

```
backend/
├── functions/           # Lambda function handlers
│   ├── auth/           # Authentication functions
│   ├── crew/           # Crew member management
│   ├── boat/           # Boat registration
│   ├── payment/        # Payment processing
│   ├── admin/          # Admin operations
│   ├── notifications/  # Notification system
│   ├── contact/        # Contact form
│   └── init/           # Initialization functions
├── shared/             # Shared utilities and libraries
│   ├── database.py     # DynamoDB operations
│   ├── configuration.py # Configuration management
│   ├── validation.py   # Input validation
│   └── notifications.py # Notification helpers
├── tests/              # Test suite
├── requirements.txt    # Python dependencies
├── Makefile           # Development commands
└── pytest.ini         # Pytest configuration
```

## Quick Start

### Setup

```bash
# Create virtual environment and install dependencies
make setup

# Or manually:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Development

```bash
# Run tests
make test

# Run tests with coverage
make test-cov

# Clean up
make clean

# Show all commands
make help
```

## Testing

Tests are located in the `tests/` directory. See [tests/README.md](tests/README.md) for detailed testing documentation.

```bash
# Run all tests
make test

# Run with coverage report
make test-cov

# Run specific test file
venv/bin/pytest tests/test_placeholder.py

# Run with markers
venv/bin/pytest -m unit
```

## Lambda Functions

Each Lambda function is organized in its own directory under `functions/`:

- **auth/**: User authentication and registration
- **crew/**: Crew member CRUD operations
- **boat/**: Boat registration and seat assignment
- **payment/**: Stripe payment integration
- **admin/**: Admin configuration and validation
- **notifications/**: Email and Slack notifications
- **contact/**: Contact form submission
- **init/**: Database initialization

## Shared Utilities

Common code is in the `shared/` directory:

- **database.py**: DynamoDB helper functions
- **configuration.py**: Configuration management from DynamoDB
- **validation.py**: Input validation with Cerberus
- **notifications.py**: Email and Slack notification helpers

## Dependencies

Key dependencies (see requirements.txt for full list):

- **boto3**: AWS SDK for Python
- **cerberus**: Data validation
- **stripe**: Payment processing
- **jinja2**: Email templating
- **pytest**: Testing framework
- **moto**: AWS service mocking for tests

## Environment Variables

Lambda functions use these environment variables:

- `TABLE_NAME`: DynamoDB table name
- `AWS_REGION`: AWS region (default: eu-west-3)
- `STRIPE_SECRET_KEY`: Stripe API key
- `ENVIRONMENT`: Environment name (dev/prod)

## Development Workflow

1. Create/modify Lambda function in `functions/`
2. Add shared utilities to `shared/` if needed
3. Write tests in `tests/`
4. Run tests: `make test`
5. Deploy via CDK from `infrastructure/`

## Code Style

- Follow PEP 8 style guide
- Use type hints where appropriate
- Add docstrings to functions
- Keep functions focused and small
- Use descriptive variable names

## Error Handling

All Lambda functions should:

1. Validate input data
2. Handle exceptions gracefully
3. Return standardized error responses
4. Log errors to CloudWatch

Example:
```python
def lambda_handler(event, context):
    try:
        # Validate input
        body = json.loads(event['body'])
        validate_input(body)
        
        # Process request
        result = process_request(body)
        
        return {
            'statusCode': 200,
            'body': json.dumps(result)
        }
    except ValidationError as e:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': str(e)})
        }
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error'})
        }
```

## Logging

Use Python's logging module:

```python
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

logger.info("Processing request")
logger.error("Error occurred", exc_info=True)
```

## Local Testing

Test Lambda functions locally:

```python
from functions.crew.create_crew_member import lambda_handler

event = {
    'body': json.dumps({
        'first_name': 'John',
        'last_name': 'Doe',
        # ...
    })
}

response = lambda_handler(event, None)
print(response)
```

## Deployment

Lambda functions are deployed via AWS CDK from the `infrastructure/` directory:

```bash
cd ../infrastructure
cdk deploy --all --context env=dev
```

## Troubleshooting

### Import errors
Ensure virtual environment is activated:
```bash
source venv/bin/activate
```

### AWS credential errors
Configure AWS credentials:
```bash
aws configure
```

### Test failures
Check test output and logs:
```bash
make test-cov
```

## Resources

- [AWS Lambda Python](https://docs.aws.amazon.com/lambda/latest/dg/lambda-python.html)
- [Boto3 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
- [Pytest Documentation](https://docs.pytest.org/)
