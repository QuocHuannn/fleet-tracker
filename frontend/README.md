# Fleet Tracker Frontend

React-based frontend application for the Fleet Tracker GPS vehicle tracking system.

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ (or Docker)
- Backend services running (see main README)

### Development Setup

#### Option 1: Using Docker (Recommended)
```bash
# From project root
./scripts/dev-frontend.sh
```

#### Option 2: Local Development
```bash
cd frontend
npm install
npm start
```

The application will be available at `http://localhost:3000`

## 📁 Project Structure

```
frontend/
├── public/                 # Static files
├── src/
│   ├── components/         # Reusable components
│   │   ├── Auth/          # Authentication components
│   │   ├── Dashboard/     # Dashboard components
│   │   ├── Layout/        # Layout components
│   │   ├── Map/           # Map components
│   │   └── Vehicles/      # Vehicle management components
│   ├── contexts/          # React contexts
│   ├── hooks/             # Custom hooks
│   ├── pages/             # Page components
│   ├── services/          # API services
│   ├── types/             # TypeScript types
│   └── utils/             # Utility functions
├── package.json
└── README.md
```

## 🔧 Available Scripts

- `npm start` - Start development server
- `npm build` - Build for production
- `npm test` - Run tests
- `npm run lint` - Run ESLint
- `npm run type-check` - Run TypeScript type checking

## 🌐 Environment Variables

Create a `.env` file in the frontend directory:

```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8004/ws
REACT_APP_FIREBASE_API_KEY=your_firebase_api_key
REACT_APP_FIREBASE_AUTH_DOMAIN=your_firebase_auth_domain
REACT_APP_FIREBASE_PROJECT_ID=your_firebase_project_id
REACT_APP_FIREBASE_STORAGE_BUCKET=your_firebase_storage_bucket
REACT_APP_FIREBASE_MESSAGING_SENDER_ID=your_firebase_messaging_sender_id
REACT_APP_FIREBASE_APP_ID=your_firebase_app_id
```

## 🗺️ Features

- **Authentication**: Login/Register with Firebase
- **Dashboard**: Real-time vehicle tracking overview
- **Live Map**: Interactive map with vehicle locations
- **Vehicle Management**: CRUD operations for vehicles
- **Real-time Updates**: WebSocket integration
- **Responsive Design**: Mobile-friendly interface

## 🔌 API Integration

The frontend integrates with the following backend services:

- **API Gateway** (`:8000`): Main entry point
- **Auth Service** (`:8001`): Authentication & authorization
- **Vehicle Service** (`:8002`): Vehicle management
- **Location Service** (`:8003`): GPS data & geofencing
- **Notification Service** (`:8004`): Real-time notifications

## 🛠️ Development

### Adding New Components

1. Create component in appropriate directory under `src/components/`
2. Export from `src/components/index.ts`
3. Import and use in pages

### API Service Pattern

```typescript
// src/services/exampleService.ts
import { apiClient } from './apiClient';

export const exampleService = {
  async getData() {
    const response = await apiClient.get('/api/endpoint');
    return response.data;
  }
};
```

### State Management

- **Local State**: React hooks (`useState`, `useReducer`)
- **Global State**: React Context API
- **Server State**: Custom hooks with API calls

## 🧪 Testing

```bash
# Run all tests
npm test

# Run tests in watch mode
npm test -- --watch

# Run tests with coverage
npm test -- --coverage
```

## 📦 Build & Deploy

```bash
# Build for production
npm run build

# Preview production build
npm run analyze
```

## 🤝 Contributing

1. Follow the existing code style
2. Add TypeScript types for new features
3. Write tests for new components
4. Update documentation as needed

## 📄 License

This project is part of the Fleet Tracker system.
