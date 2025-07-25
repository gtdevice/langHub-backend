# Frontend Developer Guide - LangHub API Documentation

## Overview
This guide provides comprehensive documentation for frontend developers integrating with the LangHub backend API. The API is built with FastAPI and uses Supabase for authentication and database operations.

## Base URL
- **Development**: `http://localhost:8000`
- **Production**: Check your deployment URL
- **API Version**: `/api/v1`

## Authentication
The API uses JWT Bearer token authentication. All protected endpoints require an Authorization header with the format:
```
Authorization: Bearer <your_jwt_token>
```

### Getting Started
1. **Sign In**: Use the `/api/v1/auth/signin` endpoint to obtain an access token
2. **Store Token**: Save the access token securely (localStorage, secure storage, etc.)
3. **Include Token**: Add the token to all subsequent requests in the Authorization header

---

## API Endpoints

### 🔐 Authentication Endpoints

#### POST /api/v1/auth/signin
Sign in with email and password to obtain an access token.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "userpassword"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "user-uuid",
    "email": "user@example.com",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  },
  "expires_in": 3600
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid credentials
- `500 Internal Server Error`: Server-side authentication failure

---

### 👤 User Management Endpoints

#### GET /api/v1/users/me
Get current authenticated user information.

**Headers Required:**
- `Authorization: Bearer <token>`

**Response:**
```json
{
  "user": {
    "id": "user-uuid",
    "email": "user@example.com",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
```

#### GET /api/v1/users/profile
Get simplified user profile information.

**Headers Required:**
- `Authorization: Bearer <token>`

**Response:**
```json
{
  "id": "user-uuid",
  "email": "user@example.com",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

---

### ⚙️ User Settings Endpoints

#### POST /api/v1/user-settings/
Create new user settings for the authenticated user.

**Headers Required:**
- `Authorization: Bearer <token>`

**Request:**
```json
{
  "main_language": "English",
  "learning_language": "Spanish",
  "language_level": "B1",
  "preferred_categories": ["Technology", "Travel", "Culture"]
}
```

**Response:**
```json
{
  "id": 1,
  "user_id": "user-uuid",
  "main_language": "English",
  "learning_language": "Spanish",
  "language_level": "B1",
  "preferred_categories": ["Technology", "Travel", "Culture"],
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### GET /api/v1/user-settings/me
Get current user settings.

**Headers Required:**
- `Authorization: Bearer <token>`

**Response:** Same as POST response

#### PUT /api/v1/user-settings/me
Update user settings.

**Headers Required:**
- `Authorization: Bearer <token>`

**Request:** Any subset of user settings fields
```json
{
  "language_level": "B2",
  "preferred_categories": ["Technology", "Business"]
}
```

**Response:** Updated user settings object

#### DELETE /api/v1/user-settings/me
Delete user settings.

**Headers Required:**
- `Authorization: Bearer <token>`

**Response:** 204 No Content

---

### 📰 Article Endpoints

#### GET /api/v1/articles/
Get a list of articles with optional filters. Returns up to 3 articles.

**Query Parameters:**
- `category` (optional): Filter by category (e.g., "Technology", "Travel")
- `language` (optional): Filter by language code (e.g., "en", "es")
- `level` (optional): Filter by level (e.g., "A1", "A2", "B1", "B2", "C1", "C2")

**Example:** `/api/v1/articles/?category=Technology&language=es&level=B1`

**Response:**
```json
[
  {
    "id": 1,
    "original_article_id": 101,
    "language": "es",
    "level": "B1",
    "title": "Tecnología Moderna",
    "thumbnail_url": "https://example.com/image.jpg",
    "intro": "Introduction to modern technology...",
    "adapted_text": "Full article text adapted for B1 level...",
    "metadata": {
      "word_count": 500,
      "reading_time": 5,
      "topics": ["technology", "innovation"]
    },
    "dialogue_starter_question": "What do you think about modern technology?"
  }
]
```

---

### 💬 Dialog/Conversation Endpoints

#### GET /api/v1/dialogs/{adapted_article_id}
Get or create a dialog for a specific article.

**Headers Required:**
- `Authorization: Bearer <token>`

**Path Parameters:**
- `adapted_article_id`: The ID of the adapted article

**Response:**
```json
{
  "dialogId": "dialog-uuid",
  "article": {
    "id": 1,
    "original_article_id": 101,
    "language": "es",
    "level": "B1",
    "title": "Tecnología Moderna",
    "thumbnail_url": "https://example.com/image.jpg",
    "intro": "Introduction...",
    "adapted_text": "Full article text...",
    "metadata": {},
    "dialogue_starter_question": "What do you think?"
  },
  "messages": [
    {
      "messageId": "msg-uuid-1",
      "sender": "coach",
      "text": "Welcome! Let's discuss this article.",
      "metadata": {"type": "welcome"},
      "timestamp": "2024-01-01T00:00:00Z"
    }
  ]
}
```

#### POST /api/v1/dialogs/{dialog_id}/messages
Send a message to an existing dialog.

**Headers Required:**
- `Authorization: Bearer <token>`

**Path Parameters:**
- `dialog_id`: The ID of the dialog

**Request:**
```json
{
  "message": "I think technology is very helpful for learning languages."
}
```

**Response:**
```json
[
  {
    "messageId": "msg-uuid-2",
    "sender": "user",
    "text": "I think technology is very helpful for learning languages.",
    "metadata": {"type": "user_message"},
    "timestamp": "2024-01-01T00:01:00Z"
  },
  {
    "messageId": "msg-uuid-3",
    "sender": "coach",
    "text": "Great point! Technology has revolutionized language learning...",
    "metadata": {
      "type": "coach_response",
      "corrections": {
        "sampleCorrection": "I think technology is very helpful for learning languages. → Technology has greatly enhanced language learning capabilities."
      }
    },
    "timestamp": "2024-01-01T00:01:05Z"
  }
]
```

---

### 🛠️ Admin Endpoints (Protected)

#### POST /api/v1/admin/article/process/{article_id}
Process an article to create adapted versions (Admin only).

**Headers Required:**
- `Authorization: Bearer <token>`

**Path Parameters:**
- `article_id`: The ID of the original article

**Request:**
```json
{
  "initial_lang": "en",
  "target_lang": "es",
  "langLevel": "B1"
}
```

**Response:** Success message string

#### POST /api/v1/admin/articles/generate-simple
Generate articles for specified categories (Admin only).

**Headers Required:**
- `Authorization: Bearer <token>`

**Request:**
```json
{
  "categories": ["Technology", "Travel", "Culture"]
}
```

**Response:**
```json
{
  "request_id": "uuid-string",
  "message": "Generation started",
  "estimated_articles": 9
}
```

#### GET /api/v1/admin/articles/generate-simple/{request_id}
Check article generation status.

**Headers Required:**
- `Authorization: Bearer <token>`

**Path Parameters:**
- `request_id`: The UUID from the generation request

**Response:**
```json
{
  "request_id": "uuid-string",
  "status": "completed",
  "categories": ["Technology", "Travel", "Culture"],
  "created_at": "2024-01-01T00:00:00Z",
  "completed_at": "2024-01-01T00:05:00Z"
}
```

---

## Error Handling

### Standard Error Response Format
All errors follow a consistent format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common HTTP Status Codes
- `200 OK`: Successful request
- `201 Created`: Resource created successfully
- `204 No Content`: Successful deletion
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Missing or invalid authentication
- `404 Not Found`: Resource not found
- `409 Conflict`: Resource already exists
- `500 Internal Server Error`: Server-side error

### Authentication Errors
- **401 Unauthorized**: 
  - "Authorization header missing"
  - "Token has expired"
  - "Invalid token"
  - "User not found"
  - "User ID not found in token"

---

## Frontend Integration Examples

### JavaScript/TypeScript Example

#### Setting up API client
```javascript
class LangHubAPI {
  constructor(baseURL, token = null) {
    this.baseURL = baseURL;
    this.token = token;
  }

  setToken(token) {
    this.token = token;
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'API request failed');
    }

    return response.json();
  }

  // Authentication
  async signIn(email, password) {
    const response = await this.request('/api/v1/auth/signin', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    
    this.setToken(response.access_token);
    return response;
  }

  // User settings
  async getUserSettings() {
    return this.request('/api/v1/user-settings/me');
  }

  async updateUserSettings(settings) {
    return this.request('/api/v1/user-settings/me', {
      method: 'PUT',
      body: JSON.stringify(settings),
    });
  }

  // Articles
  async getArticles(filters = {}) {
    const params = new URLSearchParams(filters);
    return this.request(`/api/v1/articles/?${params}`);
  }

  // Dialogs
  async getDialog(articleId) {
    return this.request(`/api/v1/dialogs/${articleId}`);
  }

  async sendMessage(dialogId, message) {
    return this.request(`/api/v1/dialogs/${dialogId}/messages`, {
      method: 'POST',
      body: JSON.stringify({ message }),
    });
  }
}

// Usage example
const api = new LangHubAPI('http://localhost:8000');

// Sign in
await api.signIn('user@example.com', 'password');

// Get user settings
const settings = await api.getUserSettings();

// Get articles
const articles = await api.getArticles({ 
  category: 'Technology', 
  language: 'es', 
  level: 'B1' 
});

// Start a dialog
const dialog = await api.getDialog(articles[0].id);

// Send a message
const messages = await api.sendMessage(dialog.dialogId, 'My response to the article');
```

### React Hook Example
```javascript
import { useState, useEffect } from 'react';

function useLangHubAPI() {
  const [api, setApi] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    const apiInstance = new LangHubAPI(process.env.REACT_APP_API_URL);
    
    // Check for stored token
    const token = localStorage.getItem('langhub_token');
    if (token) {
      apiInstance.setToken(token);
      setIsAuthenticated(true);
    }
    
    setApi(apiInstance);
  }, []);

  const signIn = async (email, password) => {
    const response = await api.signIn(email, password);
    localStorage.setItem('langhub_token', response.access_token);
    setIsAuthenticated(true);
    return response;
  };

  const signOut = () => {
    localStorage.removeItem('langhub_token');
    if (api) api.setToken(null);
    setIsAuthenticated(false);
  };

  return { api, isAuthenticated, signIn, signOut };
}
```

---

## Environment Variables for Frontend

Create a `.env` file in your frontend project:

```bash
# API Configuration
REACT_APP_API_URL=http://localhost:8000
# or for production
REACT_APP_API_URL=https://your-production-url.com

# Optional: Supabase configuration if using Supabase client directly
REACT_APP_SUPABASE_URL=your-supabase-url
REACT_APP_SUPABASE_ANON_KEY=your-supabase-anon-key
```

---

## Testing Endpoints

### Using curl
```bash
# Sign in
curl -X POST http://localhost:8000/api/v1/auth/signin \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password"}'

# Get articles (with auth token)
curl http://localhost:8000/api/v1/articles/?category=Technology \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Using Postman
1. Import the endpoints using the OpenAPI schema at: `http://localhost:8000/api/v1/openapi.json`
2. Set up authentication:
   - Type: Bearer Token
   - Token: Your JWT token from signin response

---

## Rate Limiting and Best Practices

- **Token Storage**: Store tokens securely (consider using httpOnly cookies for web apps)
- **Token Expiration**: Tokens expire after 1 hour (3600 seconds) - implement refresh logic
- **Error Handling**: Always handle 401 errors by redirecting to login
- **Loading States**: Show appropriate loading indicators during API calls
- **Retry Logic**: Implement retry logic for network failures
- **Caching**: Cache user settings and articles when appropriate
- **Pagination**: Currently articles return up to 3 items - implement pagination when needed

---

## Support and Troubleshooting

### Common Issues
1. **CORS Errors**: Ensure your frontend URL is allowed in the backend CORS settings
2. **401 Unauthorized**: Check token expiration and renewal
3. **404 Not Found**: Verify endpoint URLs and path parameters
4. **500 Internal Server Error**: Check server logs for detailed error messages

### Debug Mode
Enable debug logging in your frontend:
```javascript
// Add to your API client
async request(endpoint, options = {}) {
  console.log(`Making request to: ${endpoint}`);
  console.log('Options:', options);
  
  // ... rest of the request logic
  
  if (!response.ok) {
    console.error('API Error:', response.status, response.statusText);
    const error = await response.json();
    console.error('Error details:', error);
  }
}
```

---

## API Version
- **Current Version**: v1
- **Base Path**: `/api/v1`
- **OpenAPI Schema**: Available at `/api/v1/openapi.json`

Last updated: July 2025