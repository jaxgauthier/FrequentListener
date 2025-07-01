#!/bin/bash
# Railway Setup Script for Audio Frequency Game

echo "🚂 Setting up Audio Frequency Game for Railway deployment..."

# Check if we're in the right directory
if [ ! -f "app/__init__.py" ]; then
    echo "❌ Please run this script from the project root directory"
    exit 1
fi

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "📁 Initializing git repository..."
    git init
    git add .
    git commit -m "Initial commit for Railway deployment"
fi

# Check if files exist
echo "📋 Checking required files..."

required_files=(
    "railway.json"
    "Procfile"
    "requirements.txt"
    "runtime.txt"
    "app/__init__.py"
    "app/config.py"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ Missing: $file"
        exit 1
    fi
done

# Generate a secure secret key
echo "🔑 Generating secure secret key..."
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')

echo ""
echo "🎉 Setup complete! Your app is ready for Railway deployment."
echo ""
echo "📝 Next steps:"
echo "1. Push your code to GitHub:"
echo "   git add ."
echo "   git commit -m 'Prepare for Railway deployment'"
echo "   git push origin main"
echo ""
echo "2. Go to railway.app and create a new project"
echo "3. Connect your GitHub repository"
echo "4. Add these environment variables in Railway:"
echo ""
echo "   FLASK_ENV=production"
echo "   SECRET_KEY=$SECRET_KEY"
echo "   DATABASE_URL=postgresql://... (Railway will provide this)"
echo ""
echo "5. Add a PostgreSQL database service"
echo "6. Deploy and initialize the database"
echo ""
echo "📖 See RAILWAY_DEPLOYMENT.md for detailed instructions" 