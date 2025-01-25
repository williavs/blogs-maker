# Setup Guide

This guide will help you set up the AI-powered blog and invoice generator application.

## Prerequisites

- Python 3.8 or higher
- A Supabase account
- An Anthropic API key (for Claude)
- Git (for cloning the repository)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd 0-lite-llm-agents
```

2. Create a virtual environment and install dependencies:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
pip install -r requirements.txt
```

## Supabase Configuration

### Database Setup

1. Create a new project in Supabase
2. Set up the following tables:

#### Posts Table
```sql
create table posts (
  id uuid default uuid_generate_v4() primary key,
  title text not null,
  description text,
  content text,
  type text,
  thumbnail text,
  tags text[],
  published boolean default false,
  created_at timestamp with time zone default timezone('utc'::text, now()),
  updated_at timestamp with time zone default timezone('utc'::text, now())
);
```

### Storage Setup

1. Create a new bucket called `blog-assets`
2. Set the bucket's privacy setting to public
3. Create a folder within the bucket called `blog-images`
4. Set up the following storage policies:

```sql
-- Allow public access to view files
CREATE POLICY "Give public access to blog-assets" ON storage.objects
  FOR SELECT TO public USING (bucket_id = 'blog-assets');

-- Allow authenticated users to upload files
CREATE POLICY "Allow uploads to blog-assets" ON storage.objects
  FOR INSERT TO authenticated USING (bucket_id = 'blog-assets');
```

## Environment Configuration

1. Create a `.streamlit/secrets.toml` file with the following content:
```toml
SUPABASE_URL = "your-supabase-project-url"
SUPABASE_KEY = "your-supabase-anon-key"
ANTHROPIC_API_KEY = "your-anthropic-api-key"

# Bank details for invoices
BANK_NAME = "Your Bank Name"
BANK_ADDRESS = "Your Bank Address"
ACCOUNT_TYPE = "Checking"
ROUTING_NUMBER = "Your Routing Number"
ACCOUNT_NUMBER = "Your Account Number"
```

## Running the Application

1. Make the startup script executable:
```bash
chmod +x start_app.sh
```

2. Start the application:
```bash
./start_app.sh
```

The application will be available at `http://localhost:8501`

## Features

### Blog Management
- Create and edit blog posts
- Upload and manage post images
- Toggle post publish status
- Tag-based organization

### Invoice Generator
- AI-powered time entry processing
- Professional PDF invoice generation
- Automatic calculations
- Client information management

## Troubleshooting

### Common Issues

1. **Image Upload Issues**
   - Ensure the `blog-assets` bucket is public
   - Check storage policies are correctly set
   - Verify file permissions

2. **Database Connection Issues**
   - Confirm Supabase credentials in secrets.toml
   - Check if the database is online
   - Verify table structures

3. **Invoice Generation Issues**
   - Ensure all required fields are filled
   - Check bank details in secrets.toml
   - Verify PDF output directory permissions 