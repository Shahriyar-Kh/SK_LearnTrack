#!/bin/bash
# FILE: reset_database.sh
# ============================================================================
# Complete database reset script
# Run with: bash reset_database.sh
# ============================================================================

echo "======================================================================"
echo "SK-LearnTrack Database Reset Script"
echo "======================================================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Database credentials (update these)
DB_NAME="sklearntrack_db"
DB_USER="postgres"
DB_PASSWORD="postgres"
DB_HOST="localhost"
DB_PORT="5432"

echo -e "${YELLOW}Step 1: Stopping any running Django processes...${NC}"
pkill -f "python manage.py runserver" 2>/dev/null || true
sleep 2

echo -e "${YELLOW}Step 2: Deleting old migration files...${NC}"
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete
echo -e "${GREEN}✓ Migration files deleted${NC}"

echo -e "${YELLOW}Step 3: Dropping and recreating database...${NC}"
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -c "DROP DATABASE IF EXISTS $DB_NAME;"
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -c "CREATE DATABASE $DB_NAME;"
echo -e "${GREEN}✓ Database recreated${NC}"

echo -e "${YELLOW}Step 4: Creating new migrations...${NC}"
python manage.py makemigrations accounts
python manage.py makemigrations courses
python manage.py makemigrations notes
python manage.py makemigrations roadmaps
python manage.py makemigrations analytics
echo -e "${GREEN}✓ Migrations created${NC}"

echo -e "${YELLOW}Step 5: Applying migrations...${NC}"
python manage.py migrate
echo -e "${GREEN}✓ Migrations applied${NC}"

echo -e "${YELLOW}Step 6: Creating superuser...${NC}"
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin@example.com', 'admin123', full_name='Admin User', country='USA', education_level='postgraduate', field_of_study='Administration') if not User.objects.filter(email='admin@example.com').exists() else print('Superuser already exists')" | python manage.py shell
echo -e "${GREEN}✓ Superuser created${NC}"
echo "   Email: admin@example.com"
echo "   Password: admin123"

echo -e "${YELLOW}Step 7: Creating test student user...${NC}"
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_user('student@example.com', 'student123', full_name='Test Student', country='USA', education_level='undergraduate', field_of_study='Computer Science', terms_accepted=True) if not User.objects.filter(email='student@example.com').exists() else print('Test student already exists')" | python manage.py shell
echo -e "${GREEN}✓ Test student created${NC}"
echo "   Email: student@example.com"
echo "   Password: student123"

echo ""
echo "======================================================================"
echo -e "${GREEN}✓ Database reset complete!${NC}"
echo "======================================================================"
echo ""
echo "Next steps:"
echo "1. Run: python manage.py runserver"
echo "2. Test authentication with created users"
echo "3. Run: python test-api.py (to test all endpoints)"
echo ""