# Deploying Trade Mart to Vercel

This guide will help you deploy the Trade Mart application to Vercel.

## Prerequisites

1. A Vercel account (sign up at [vercel.com](https://vercel.com))
2. Git installed on your local machine
3. The Trade Mart repository cloned to your local machine

## Deployment Steps

### 1. Prepare Your Project

The project has already been configured for Vercel deployment with the following files:

- `vercel.json` - Configuration file for Vercel
- `api/index.py` - Entry point for the Vercel serverless function
- `api/db_init.py` - Database initialization script
- `.env.example` - Example environment variables

### 2. Push Your Code to a Git Repository

Vercel works best with Git repositories. Push your code to GitHub, GitLab, or Bitbucket.

```bash
git add .
git commit -m "Prepare for Vercel deployment"
git push
```

### 3. Deploy to Vercel

1. Log in to your Vercel account
2. Click "New Project"
3. Import your Git repository
4. Configure the project:
   - Framework Preset: Other
   - Build Command: Leave empty (handled by vercel.json)
   - Output Directory: Leave empty
   - Install Command: `pip install -r requirements.txt`

### 4. Environment Variables

Add the following environment variables in the Vercel project settings:

- `SECRET_KEY`: A secure random string for Flask's secret key
- `SQLALCHEMY_DATABASE_URI`: Your database connection string
- `DEBUG`: Set to `False` for production

### 5. Database Considerations

Vercel's serverless functions run in an ephemeral environment, which means:

1. The local SQLite database will not persist between function invocations
2. For production, you should use a hosted database service like:
   - PostgreSQL on Supabase, Neon, or Railway
   - MySQL on PlanetScale
   - MongoDB Atlas

Update your `SQLALCHEMY_DATABASE_URI` environment variable with your hosted database connection string.

### 6. Deployment Complete

Once deployed, Vercel will provide you with a URL for your application. You can also configure a custom domain in the Vercel project settings.

## Troubleshooting

- If you encounter any issues with database connections, check your environment variables and database configuration.
- For application errors, check the Vercel logs in the project dashboard.
- Remember that file uploads will not work with the default configuration as Vercel functions are stateless. Consider using a service like AWS S3 for file storage.

## Local Development

For local development, you can still use the original `run.py` script:

```bash
python run.py
```

This will run the application locally with a SQLite database.