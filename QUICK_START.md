# SK-LearnTrack: 5-Minute Quick Start Guide
# ============================================================================
# Get the system running in minimal time
# ============================================================================

## 🚀 Backend Setup (5 minutes)

### 1. Install Dependencies (1 min)
```bash
cd sklearntrack_backend
pip install -r requirements.txt
pip install groq  # For AI features
```

### 2. Apply Migrations (1 min)
```bash
python manage.py makemigrations courses
python manage.py migrate
python manage.py createsuperuser  # Create admin user
```

### 3. Setup Groq API (1 min)
```bash
# Visit https://console.groq.com/keys (FREE, no credit card)
# Get API key, then:
echo "GROQ_API_KEY=gsk_your_key_here" >> .env
```

### 4. Start Server (1 min)
```bash
python manage.py runserver
# Server runs at http://localhost:8000
```

### 5. Test Admin API (1 min)
```bash
# Get token (replace username/password)
curl -X POST http://localhost:8000/api-token-auth/ \
  -d "username=admin&password=admin"

# Create course
curl -X POST http://localhost:8000/api/admin/courses/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Python Basics",
    "description": "Learn Python fundamentals",
    "category": "programming",
    "difficulty": "beginner",
    "estimated_hours": 20
  }'
```

---

## 🎨 Frontend Setup (3 minutes)

### 1. Install Dependencies (1 min)
```bash
cd sklearntrack-frontend
npm install
npm install @dnd-kit/core @dnd-kit/sortable
npm install react-markdown react-syntax-highlighter
```

### 2. Configure API URL (30 sec)
```bash
# Create .env.local
echo "REACT_APP_API_URL=http://localhost:8000/api" > .env.local
```

### 3. Start Dev Server (1.5 min)
```bash
npm run dev
# Frontend runs at http://localhost:5173
```

---

## ✅ Verify Everything Works

### Backend Verification
```bash
# Get all published courses
curl http://localhost:8000/api/courses/

# Get admin courses
curl -H "Authorization: Token YOUR_TOKEN" \
     http://localhost:8000/api/admin/courses/

# Check migrations applied
python manage.py showmigrations courses
```

### Frontend Verification
- Open http://localhost:5173
- Should see home page
- Login with your admin credentials
- Navigate to admin section

---

## 📚 Key Files to Review

**In this order:**

1. **[COMPLETE_SYSTEM_GUIDE.md](d:/Django Projects/SK_LearnTrack/COMPLETE_SYSTEM_GUIDE.md)** (5 min)
   - Overview of everything delivered
   - File structure
   - API summary

2. **[ARCHITECTURE.md](d:/Django Projects/SK_LearnTrack/ARCHITECTURE.md)** (15 min)
   - Complete system design
   - Database schema
   - API architecture
   - Performance strategy

3. **[courses/models.py](d:/Django Projects/SK_LearnTrack/sklearntrack_backend/courses/models.py)** (10 min)
   - Data models
   - Relationships
   - Business logic

4. **[courses/urls.py](d:/Django Projects/SK_LearnTrack/sklearntrack_backend/courses/urls.py)** (5 min)
   - All API endpoints
   - Clear documentation

5. **[REACT_COMPONENTS.md](d:/Django Projects/SK_LearnTrack/REACT_COMPONENTS.md)** (15 min)
   - Frontend component structure
   - Code examples

6. **[courses/AI_SERVICE.md](d:/Django Projects/SK_LearnTrack/sklearntrack_backend/courses/AI_SERVICE.md)** (5 min)
   - AI integration (FREE!)
   - How to use Groq API

---

## 🎯 First Implementation Task

### Create Your First Course (10 min)

```python
# In Django shell
python manage.py shell

from courses.models import Course, CourseChapter, CourseTopic, CourseStatus
from django.contrib.auth.models import User

# Get admin user
admin = User.objects.first()

# Create course
course = Course.objects.create(
    title="Python Basics",
    slug="python-basics",
    description="Learn Python from scratch",
    category="programming",
    difficulty="beginner",
    estimated_hours=20,
    meta_title="Learn Python - Beginner Course",
    meta_description="Comprehensive Python tutorial for beginners",
    created_by=admin
)

# Create chapter
chapter = CourseChapter.objects.create(
    course=course,
    title="Introduction to Python",
    slug="intro-to-python",
    description="Get started with Python",
    order_index=0
)

# Create topic
topic = CourseTopic.objects.create(
    chapter=chapter,
    title="What is Python?",
    slug="what-is-python",
    content="""
# What is Python?

Python is a high-level, interpreted programming language known for its simplicity.

## Key Features

- **Easy to Learn**: Simple syntax similar to English
- **Versatile**: Web, data science, automation, AI
- **Large Community**: Lots of libraries and support

## Example

```python
print("Hello, World!")
```
""",
    estimated_minutes=15,
    difficulty="beginner",
    order_index=0
)

# Publish course
course.status = CourseStatus.PUBLISHED
course.save()

print(f"Course created: {course.title}")
```

---

## 🧪 Test The Full Flow

### As Admin (Course Creator)
1. Login at `/admin/`
2. See course in admin panel
3. Create new course
4. Add chapters and topics
5. Publish course

### As Student
1. Login with regular user
2. Browse courses at `/courses/`
3. Enroll in a course
4. View topics
5. Complete quiz
6. Track progress

---

## 🤖 Test AI Features (Optional)

```bash
# Generate course outline
curl -X POST http://localhost:8000/api/admin/ai/generate-outline/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Python Basics",
    "level": "beginner"
  }'

# Should get back structured course outline with chapters and topics
```

---

## 📊 Database

### View Data in Django Admin
- Go to http://localhost:8000/admin/
- Login with superuser credentials
- Browse:
  - Courses
  - Chapters  
  - Topics
  - Quiz attempts
  - Enrollments
  - Audit logs

---

## 🆘 Common Issues

### "No such table" Error
```bash
python manage.py migrate courses
```

### Token Auth Not Working
```bash
# Make sure TokenAuthentication is in settings.py
INSTALLED_APPS = [
    'rest_framework.authtoken',
    ...
]

# Create token
python manage.py drf_create_token username
```

### API Returns 403 Forbidden
- Make sure user is staff/admin for admin endpoints
- Make sure user is authenticated for student endpoints

### Frontend can't reach API
- Check REACT_APP_API_URL in .env.local
- Make sure backend server is running
- Check CORS settings in Django settings.py

---

## 📈 What to Do Next

### Week 1
- [ ] Run migrations successfully
- [ ] Create test course via API
- [ ] Test admin and student endpoints
- [ ] Setup Groq API
- [ ] Test AI outline generation

### Week 2
- [ ] Build admin course builder UI
- [ ] Build student learning UI
- [ ] Connect React to backend APIs
- [ ] Test full course creation flow

### Week 3
- [ ] Implement quiz grading
- [ ] Implement progress tracking
- [ ] Polish UI/UX
- [ ] Performance optimization

### Week 4+
- [ ] Deploy to Render + Vercel
- [ ] User testing & feedback
- [ ] Bug fixes & refinement
- [ ] Feature enhancements

---

## 💡 Pro Tips

1. **Use Django Admin**: Edit data quickly during testing
2. **API Documentation**: Use Postman/Insomnia for API testing
3. **Database**: Use `python manage.py dbshell` for SQL queries
4. **Frontend**: React DevTools for state debugging
5. **Logs**: Check console for migration errors

---

## 🎉 You're Ready!

You have everything needed to:
- Build world-class eLearning platform
- Scale to millions of users
- Use FREE AI for content generation
- Deploy to production
- Monitor and improve

**Start coding! 🚀**

---

**Questions?** 
- Check ARCHITECTURE.md for design decisions
- Check IMPLEMENTATION_CHECKLIST.md for detailed steps
- Check specific .md files for feature guides

**Good luck! 🍀**
