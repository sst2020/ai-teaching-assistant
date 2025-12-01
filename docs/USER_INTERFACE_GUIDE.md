# AI Teaching Assistant - User Interface Guide

This guide provides comprehensive documentation for the AI Teaching Assistant MVP user interface, including page descriptions, workflows, and accessibility features.

## Table of Contents

1. [Overview](#overview)
2. [Pages and Components](#pages-and-components)
3. [User Workflows](#user-workflows)
4. [Accessibility Features](#accessibility-features)
5. [Material Design 3 Theme](#material-design-3-theme)

---

## Overview

The AI Teaching Assistant is a web-based application designed to help students submit assignments, receive AI-powered feedback, and track their academic progress. The interface follows Material Design 3 (MD3) principles for a modern, accessible user experience.

### Technology Stack
- **Frontend**: React 19 with TypeScript
- **Styling**: CSS with MD3 design tokens
- **Code Editor**: Monaco Editor (VS Code's editor)
- **Routing**: React Router v7
- **State Management**: React Context API

---

## Pages and Components

### 1. Login Page (`/login`)

**Purpose**: Authenticate existing users to access the system.

**Components**:
- Email input field with validation
- Password input field with visibility toggle
- "Remember me" checkbox
- Login button with loading state
- Link to registration page

**Features**:
- Form validation with error messages
- Toast notifications for success/failure
- Automatic redirect to dashboard on success
- Keyboard navigation support (Tab, Enter)

---

### 2. Registration Page (`/register`)

**Purpose**: Create new user accounts.

**Components**:
- Name input field
- Email input field with format validation
- Password input with strength indicator
- Confirm password field
- Role selector (Student/Teacher)
- Register button with loading state

**Features**:
- Real-time password match validation
- Email format validation
- Toast notifications for feedback
- Link to login page for existing users

---

### 3. Dashboard (`/dashboard`)

**Purpose**: Main landing page showing system overview and quick actions.

**Components**:
- Welcome header with user name
- Quick action cards (Submit Assignment, View Grades, Q&A)
- Recent activity feed
- Statistics summary

**Features**:
- Responsive grid layout
- Card-based navigation
- Real-time data updates

---

### 4. Student Dashboard (`/student-dashboard`)

**Purpose**: Student-specific view with personalized statistics and assignments.

**Components**:
- Profile summary card
- Course enrollment list
- Assignment progress tracker
- Grade summary with averages
- Upcoming deadlines widget

**Features**:
- Personalized statistics
- Progress visualization
- Quick links to pending assignments

---

### 5. Submit Assignment Page (`/submit/:assignmentId`)

**Purpose**: Submit code assignments with integrated code editor.

**Components**:
- Assignment details panel (title, description, due date)
- Monaco Code Editor with syntax highlighting
- Language selector dropdown
- File upload zone (drag & drop)
- Rubric display panel
- Submit and Clear buttons with confirmation dialogs

**Features**:
- **Monaco Editor Integration**: Full-featured code editor with:
  - Syntax highlighting for 10+ languages
  - Line numbers and minimap
  - Auto-indentation
  - Find and replace
- **File Upload**: Drag-and-drop or click to upload
  - Supports: .py, .java, .cpp, .js, .ts, .c, .cs, .go, .rb, .php
  - Automatic language detection
- **Auto-save**: Drafts saved to localStorage every 30 seconds
- **Keyboard Shortcuts**: Ctrl+S to save draft
- **Confirmation Dialogs**: Prevent accidental submission/clear

---

### 6. Grades Page (`/grades`)

**Purpose**: View submission history and detailed feedback.

**Components**:
- Grade distribution chart (bar chart visualization)
- Submissions table with sorting and filtering
- Grade letter badges (A, B, C, D, F with colors)
- Detailed submission modal
- Filter controls (by assignment, date range, grade)
- Sort controls (by date, grade, assignment)

**Features**:
- **Grade Distribution Chart**: Visual breakdown of grades
- **Sortable Table**: Click headers to sort
- **Filtering**: Filter by assignment or grade range
- **Detailed Modal**: Click any submission to see:
  - Full feedback text
  - Category-based scores
  - Submitted code
  - Timestamp information
- **URL Deep Linking**: Share links to specific submissions

---

### 7. Code Analysis (`/code-analysis`)

**Purpose**: Get AI-powered analysis of code snippets.

**Components**:
- Code input area
- Language selector
- Analysis results panel
- Suggestions list

**Features**:
- Real-time code analysis
- Style and best practice suggestions
- Error detection

---

### 8. Q&A Interface (`/qa`)

**Purpose**: Ask questions and get AI-powered answers.

**Components**:
- Question input field
- Conversation history
- Answer display with formatting
- Related topics suggestions

**Features**:
- Natural language question input
- Formatted answer display
- Conversation context retention

---

## User Workflows

### Workflow 1: First-Time User Registration

1. Navigate to `/register`
2. Fill in name, email, and password
3. Select role (Student)
4. Click "Register"
5. Receive success notification
6. Automatically redirected to login

### Workflow 2: Submitting an Assignment

1. Log in to the system
2. Navigate to Dashboard
3. Click on an assignment or go to `/submit/:assignmentId`
4. View assignment details and rubric
5. Either:
   - Type code directly in Monaco Editor, OR
   - Upload a code file via drag-and-drop
6. Select the programming language
7. Click "Submit Assignment"
8. Confirm in the dialog
9. Receive success notification

### Workflow 3: Viewing Grades and Feedback

1. Navigate to `/grades`
2. View grade distribution chart
3. Use filters to find specific submissions
4. Click on a submission row
5. View detailed feedback in modal
6. Close modal to return to list

### Workflow 4: Getting Help via Q&A

1. Navigate to `/qa`
2. Type your question
3. Submit and wait for AI response
4. View formatted answer
5. Ask follow-up questions as needed

---

## Accessibility Features

The application implements comprehensive accessibility features following WCAG 2.1 guidelines.

### Keyboard Navigation

| Key | Action |
|-----|--------|
| `Tab` | Move focus to next interactive element |
| `Shift+Tab` | Move focus to previous element |
| `Enter` | Activate buttons, submit forms |
| `Escape` | Close modals and dialogs |
| `Ctrl+S` | Save draft (in code editor) |

### ARIA Attributes

- **Roles**: Proper semantic roles for all interactive elements
- **Labels**: `aria-label` and `aria-labelledby` for screen readers
- **States**: `aria-expanded`, `aria-selected`, `aria-disabled`
- **Live Regions**: `aria-live` for dynamic content updates

### Focus Management

- **Focus Trap**: Modals and dialogs trap focus within
- **Focus Indicators**: Visible focus rings on all interactive elements
- **Focus Restoration**: Focus returns to trigger element when dialogs close

### Color and Contrast

- Minimum 4.5:1 contrast ratio for text
- Color is not the only indicator of state
- Grade badges use both color and letter indicators

### Screen Reader Support

- Semantic HTML structure
- Descriptive link text
- Form labels associated with inputs
- Error messages announced via `aria-live`

---

## Material Design 3 Theme

The application uses Material Design 3 (MD3) with an expressive theme.

### Design Tokens

```css
/* Primary Colors */
--md-sys-color-primary: #6750A4;
--md-sys-color-on-primary: #FFFFFF;
--md-sys-color-primary-container: #EADDFF;

/* Secondary Colors */
--md-sys-color-secondary: #625B71;
--md-sys-color-on-secondary: #FFFFFF;

/* Surface Colors */
--md-sys-color-surface: #FFFBFE;
--md-sys-color-surface-variant: #E7E0EC;

/* Error Colors */
--md-sys-color-error: #B3261E;
--md-sys-color-on-error: #FFFFFF;
```

### Shape System

```css
--md-sys-shape-corner-extra-small: 4px;
--md-sys-shape-corner-small: 8px;
--md-sys-shape-corner-medium: 12px;
--md-sys-shape-corner-large: 16px;
--md-sys-shape-corner-extra-large: 28px;
```

### Elevation Levels

- **Level 0**: Flat surfaces
- **Level 1**: Cards, raised buttons
- **Level 2**: App bars, menus
- **Level 3**: Dialogs, modals

### Typography

- **Display**: Large headings
- **Headline**: Section headers
- **Title**: Card titles, list items
- **Body**: Paragraph text
- **Label**: Buttons, form labels

### Component Styling

All components follow MD3 guidelines:
- **Buttons**: Filled, outlined, and text variants
- **Cards**: Elevated and filled variants
- **Inputs**: Outlined text fields with floating labels
- **Dialogs**: Centered with scrim overlay
- **Chips**: Filter and input variants

---

## Common UI Components

### LoadingSpinner
Displays during async operations with accessible loading message.

### ErrorMessage
Shows error states with retry option and descriptive text.

### Toast Notifications
Non-blocking notifications for success, error, info, and warning states.

### ConfirmDialog
Modal dialog for confirming destructive actions with:
- Customizable title and message
- Confirm and cancel buttons
- Focus trap and keyboard support
- Danger variant for destructive actions

### Skeleton Loaders
Placeholder content during data loading:
- `Skeleton`: Basic loading placeholder
- `SkeletonCard`: Card-shaped placeholder
- `SkeletonTable`: Table-shaped placeholder

---

## Responsive Design

The application is fully responsive across device sizes:

| Breakpoint | Width | Layout |
|------------|-------|--------|
| Mobile | < 600px | Single column, stacked cards |
| Tablet | 600-1024px | Two column grid |
| Desktop | > 1024px | Full layout with sidebar |

### Mobile Optimizations
- Touch-friendly button sizes (min 44x44px)
- Collapsible navigation
- Swipe gestures for modals
- Optimized code editor for mobile

---

## Browser Support

| Browser | Version | Status |
|---------|---------|--------|
| Chrome | 90+ | ✅ Fully Supported |
| Firefox | 88+ | ✅ Fully Supported |
| Safari | 14+ | ✅ Fully Supported |
| Edge | 90+ | ✅ Fully Supported |

---

## Known Limitations

1. **Offline Mode**: Not currently supported; requires internet connection
2. **File Size**: Maximum upload size is 5MB per file
3. **Languages**: Code editor supports common languages; some exotic languages may lack syntax highlighting
4. **Mobile Code Editor**: Monaco Editor has limited mobile support; file upload recommended on mobile devices

---

*Last Updated: December 2025*

