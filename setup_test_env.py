import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Create a .env file for testing
if not os.path.exists('/home/ubuntu/personal-ai-agent/.env'):
    with open('/home/ubuntu/personal-ai-agent/.env', 'w') as f:
        f.write('OPENAI_API_KEY=sk-your-openai-api-key\n')
        f.write('DB_TYPE=local\n')

# Create __init__.py files to make the modules importable
directories = [
    '/home/ubuntu/personal-ai-agent/app',
    '/home/ubuntu/personal-ai-agent/app/api',
    '/home/ubuntu/personal-ai-agent/app/api/agent',
    '/home/ubuntu/personal-ai-agent/app/core',
    '/home/ubuntu/personal-ai-agent/app/db',
    '/home/ubuntu/personal-ai-agent/app/models',
    '/home/ubuntu/personal-ai-agent/app/utils',
]

for directory in directories:
    init_file = os.path.join(directory, '__init__.py')
    if not os.path.exists(init_file):
        with open(init_file, 'w') as f:
            f.write('# Make the module importable\n')

print("Test environment setup completed.")
