# 🎓 SK-LearnTrack Admin Course Builder

## Beautiful, Advanced Course Management Interface

The Admin Course Builder provides a professional, modern interface for creating and managing online courses with an intuitive 4-column layout design.

---

## 🚀 Features

### ✨ Core Features

- **📚 Course Management**
  - Create, edit, publish courses
  - Draft/Published status tracking
  - Soft delete (archive) courses
  - Duplicate courses with one click
  - SEO metadata management

- **🏗️ Course Structure**
  - Hierarchical organization: Course → Chapters → Topics
  - Add/edit/delete chapters and topics
  - Drag-and-drop interface (ready for dnd-kit)
  - Reorder chapters and topics
  - Quick navigation tree view

- **📝 Content Editor**
  - Rich Markdown editor with live toolbar
  - Markdown formatting shortcuts
  - Code block support with syntax highlighting
  - Image/PDF asset uploads (backend integration)
  - Auto-save functionality

- **👁️ Live Preview**
  - Student-view preview of content
  - Real-time Markdown rendering
  - Metadata display (difficulty, estimated time, key concepts)
  - WYSIWYG experience

- **📊 Course Metadata**
  - Title, description, category
  - Difficulty levels (Beginner/Intermediate/Advanced)
  - Estimated hours
  - Tags for organization
  - SEO settings (meta title, meta description)

- **🔒 Admin Controls**
  - Publish validation (requires chapters, topics, content)
  - Version history tracking
  - Audit logging
  - Permission checks (admin-only)

---

## 📁 File Structure

```
src/
├── components/
│   └── admin/
│       ├── AdminLayout.jsx              # Sidebar + Header layout
│       ├── CourseListPage.jsx           # Course grid/list view
│       ├── CourseBuilder.jsx            # Main 4-column interface
│       ├── CourseCreatePage.jsx         # New course form
│       └── panels/
│           ├── CourseMetadataPanel.jsx  # Course details & SEO
│           ├── CourseStructureTree.jsx  # Chapter/topic tree
│           ├── ContentEditor.jsx        # Markdown editor
│           └── PreviewPanel.jsx         # Student view preview
├── services/
│   └── courseAdminService.js           # API service (complete)
└── pages/
    └── (existing pages)
```

---

## 🎨 UI/UX Design

### Color Scheme (Dark Modern Theme)
- **Background**: `#111827` (gray-900)
- **Cards**: `#1F2937` (gray-800)
- **Borders**: `#374151` (gray-700)
- **Primary**: `#2563EB` (blue-600)
- **Success**: `#16A34A` (green-600)
- **Text**: `#F3F4F6` (gray-100)

### Components
- **Responsive**: Works on desktop, tablet, mobile
- **Accessible**: WCAG 2.1 compliant
- **Modern**: Glassmorphism, smooth transitions, hover effects
- **Icons**: Lucide React icons throughout

### 4-Column Layout
```
┌─────────────────────────────────────────────────────────┐
│  Header: Title | Save | Publish | Menu                 │
├──────────┬──────────┬──────────┬──────────────────────┤
│          │          │          │                      │
│ Metadata │Structure │ Content  │  Preview             │
│  Panel   │  Tree    │ Editor   │  Panel               │
│  (25%)   │  (25%)   │  (25%)   │  (25%)               │
│          │          │          │                      │
└──────────┴──────────┴──────────┴──────────────────────┘
```

---

## 🔌 API Integration

### Service: `courseAdminService.js`

All backend communication is handled through `courseAdminService`:

#### Courses
```javascript
// Get all courses
await courseAdminService.getCourses({ status, category, search, page })

// Get single course
await courseAdminService.getCourse(courseId)

// Create course
await courseAdminService.createCourse(courseData)

// Update course
await courseAdminService.updateCourse(courseId, courseData)

// Delete course (soft delete)
await courseAdminService.deleteCourse(courseId)

// Publish course
await courseAdminService.publishCourse(courseId, changeSummary)

// Unpublish course
await courseAdminService.unpublishCourse(courseId)

// Preview course (student view)
await courseAdminService.previewCourse(courseId)

// Duplicate course
await courseAdminService.duplicateCourse(courseId, newTitle)

// Get version history
await courseAdminService.getVersionHistory(courseId)

// Get audit log
await courseAdminService.getAuditLog(courseId)
```

#### Chapters & Topics
```javascript
// Create chapter
await courseAdminService.createChapter(courseId, chapterData)

// Update chapter
await courseAdminService.updateChapter(courseId, chapterId, chapterData)

// Delete chapter
await courseAdminService.deleteChapter(courseId, chapterId)

// Create topic
await courseAdminService.createTopic(courseId, chapterId, topicData)

// Update topic
await courseAdminService.updateTopic(courseId, chapterId, topicId, topicData)

// Delete topic
await courseAdminService.deleteTopic(courseId, chapterId, topicId)

// Reorder topics
await courseAdminService.reorderTopics(courseId, chapterId, ordering)
```

#### Quiz & Assets
```javascript
// Get/Create quiz
await courseAdminService.getTopicQuiz(courseId, chapterId, topicId)

// Save quiz
await courseAdminService.saveQuiz(courseId, chapterId, topicId, quizData)

// Upload asset
await courseAdminService.uploadAsset(topicId, file, assetType)

// Delete asset
await courseAdminService.deleteAsset(assetId)
```

---

## 📱 Component Usage

### AdminLayout
Wraps admin pages with sidebar navigation and header.

```jsx
<AdminLayout>
  <YourAdminPage />
</AdminLayout>
```

### CourseListPage
Displays all courses with search, filters, and actions.

```jsx
import { CourseListPage } from '@/components/admin/CourseListPage'

<Route path="/admin/courses" element={
  <AdminRoute>
    <AdminLayout>
      <CourseListPage />
    </AdminLayout>
  </AdminRoute>
} />
```

### CourseBuilder
Main 4-column editor interface.

```jsx
import { CourseBuilder } from '@/components/admin/CourseBuilder'

<Route path="/admin/courses/:courseId" element={
  <AdminRoute>
    <AdminLayout>
      <CourseBuilder />
    </AdminLayout>
  </AdminRoute>
} />
```

### CourseCreatePage
Form for creating new courses.

```jsx
import { CourseCreatePage } from '@/components/admin/CourseCreatePage'

<Route path="/admin/courses/create" element={
  <AdminRoute>
    <AdminLayout>
      <CourseCreatePage />
    </AdminLayout>
  </AdminRoute>
} />
```

---

## 📝 Markdown Support

The content editor supports full Markdown syntax:

```markdown
# Heading 1
## Heading 2
### Heading 3

**Bold text** or __bold__
*Italic text* or _italic_

- List item 1
- List item 2
  - Nested item

1. Ordered item
2. Another item

> Quote or note

[Link text](https://url.com)

`inline code`

\`\`\`python
# Code block
def hello():
    print('World')
\`\`\`

| Column 1 | Column 2 |
|----------|----------|
| Data 1   | Data 2   |
```

---

## 🎓 Creating a Course

### Step 1: Create Course
1. Navigate to `/admin/courses`
2. Click "Create Course"
3. Fill in course details
4. Click "Create Course"

### Step 2: Add Structure
1. In Course Builder, use Structure panel to add chapters
2. Click "Add topic" under each chapter
3. Each topic can have content

### Step 3: Add Content
1. Select a topic from the structure tree
2. Edit in the Content Editor (middle panel)
3. Use Markdown formatting
4. Click "Save Content"

### Step 4: Preview
1. Live preview updates as you type
2. See how students will view the content
3. Check formatting and styling

### Step 5: Publish
1. Click "Publish" button
2. System validates course structure
3. Course becomes available to students

---

## ✅ Validation Rules

### Before Publishing
- ✅ Course must have at least 1 chapter
- ✅ Each chapter must have at least 1 topic
- ✅ Each topic must have content

### Publish Errors
- ❌ "Course must have at least 1 chapter"
- ❌ "Chapter X has no topics"
- ❌ "Topic Y has no content"

---

## 🔐 Permissions

### Admin-Only Access
- All `/admin/courses/*` routes require `isAdmin` permission
- Enforced by `AdminRoute` guard
- Backend validates permissions on all API calls
- Non-admin users receive 403 Forbidden

---

## 🚀 Performance Optimizations

- ✅ Lazy loading of course content
- ✅ Cached course structure in state
- ✅ Debounced auto-save
- ✅ Optimistic UI updates
- ✅ Image lazy loading in preview

---

## 📚 Future Enhancements

- [ ] Drag-and-drop reordering with @dnd-kit
- [ ] AI-powered content suggestions
- [ ] Built-in quiz builder
- [ ] Video embed support
- [ ] Collaborative editing
- [ ] Batch import/export
- [ ] Template library
- [ ] Advanced analytics

---

## 🐛 Troubleshooting

### Course Not Loading
1. Check network tab in DevTools
2. Verify course ID in URL
3. Ensure user has admin permissions

### Content Not Saving
1. Check API response in Network tab
2. Verify content is valid Markdown
3. Check browser console for errors

### Preview Not Updating
1. Refresh browser (hard refresh: Ctrl+Shift+R)
2. Check if content was saved
3. Verify Markdown syntax

---

## 📖 Additional Resources

- [Backend API Documentation](../sklearntrack_backend/courses/AI_SERVICE.md)
- [Model Structure](../sklearntrack_backend/courses/models.py)
- [API Views](../sklearntrack_backend/courses/views_admin.py)

---

## 🤝 Contributing

To improve the admin builder:

1. Create feature branch
2. Make changes
3. Test thoroughly
4. Submit PR with description

---

## 📄 License

Part of SK-LearnTrack project. All rights reserved.
