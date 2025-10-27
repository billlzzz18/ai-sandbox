---
name: Next.js Best Practices
description: Comprehensive guidelines for Next.js development following modern React patterns
---

# Next.js Best Practices & Guidelines

## 🏗️ Architecture Principles

### 1. App Router First
- **Use App Router** over Pages Router for new applications
- **Server Components by default** - Only use Client Components when necessary
- **Route Groups** for organization: `(auth)`, `(dashboard)`, `(public)`
- **Parallel Routes** for complex layouts with independent navigation

### 2. Component Architecture
- **Server Components** for data fetching and static content
- **Client Components** only for interactivity (use `'use client'`)
- **Composition over inheritance** - Use compound components and render props
- **Custom hooks** for shared logic and state management

### 3. File Organization
```
app/
├── (auth)/
│   ├── login/
│   │   ├── page.tsx
│   │   └── actions.ts
│   └── layout.tsx
├── (dashboard)/
│   ├── page.tsx
│   ├── layout.tsx
│   └── components/
│       ├── sidebar.tsx
│       └── header.tsx
└── api/
    └── users/
        └── route.ts

components/
├── ui/           # Reusable UI components
├── forms/        # Form components
├── layout/       # Layout components
└── providers/    # Context providers

lib/
├── utils/        # Utility functions
├── hooks/        # Custom hooks
├── validations/  # Zod schemas
└── types/        # TypeScript types
```

## ⚡ Performance Optimization

### 1. Server Components & SSR
- **Server Components** reduce bundle size and improve performance
- **Streaming** for progressive loading: `loading.tsx`, `suspense`
- **Static Generation** for marketing pages and blogs
- **Dynamic Rendering** for personalized content

### 2. Data Fetching
- **Server Components** for initial data fetching
- **TanStack Query** for client-side data fetching and caching
- **Optimistic Updates** for better UX
- **Error Boundaries** for graceful error handling

### 3. Image Optimization
- **Next.js Image Component** with automatic optimization
- **WebP/AVIF formats** for modern browsers
- **Responsive images** with `sizes` prop
- **Lazy loading** by default

### 4. Bundle Optimization
- **Dynamic imports** for code splitting: `import()`
- **Tree shaking** - Only import what you use
- **Bundle analyzer** to identify large dependencies
- **Route-based splitting** with App Router

## 🔒 Security Best Practices

### 1. Input Validation
- **Zod schemas** for runtime validation
- **Server-side validation** for all user inputs
- **Sanitization** of user-generated content
- **Type safety** with strict TypeScript

### 2. Authentication & Authorization
- **NextAuth.js** or similar for authentication
- **Middleware** for route protection
- **Server-side session validation**
- **CSRF protection** for forms

### 3. Data Protection
- **Environment variables** for secrets
- **API routes** for sensitive operations
- **Rate limiting** on API endpoints
- **CORS configuration** for cross-origin requests

## 🎨 UI/UX Excellence

### 1. Modern UI Frameworks
- **Tailwind CSS** for utility-first styling
- **shadcn/ui + Radix UI** for accessible components
- **Consistent design system** with design tokens
- **Dark mode support** with CSS variables

### 2. Accessibility (WCAG 2.1 AA)
- **Semantic HTML** with proper ARIA labels
- **Keyboard navigation** support
- **Screen reader** compatibility
- **Color contrast** ratios (4.5:1 minimum)
- **Focus management** in modals and forms

### 3. Responsive Design
- **Mobile-first** approach
- **Fluid typography** with `clamp()`
- **Container queries** for component-based responsive design
- **Touch-friendly** interactive elements

## 🧪 Testing Strategy

### 1. Component Testing
- **React Testing Library** for user-centric tests
- **Jest** for unit tests and mocking
- **Vitest** for faster test execution
- **Playwright** for E2E testing

### 2. Test Organization
```
__tests__/
├── unit/
│   ├── components/
│   ├── hooks/
│   └── utils/
├── integration/
│   ├── api/
│   └── workflows/
└── e2e/
    ├── auth/
    └── dashboard/
```

### 3. Testing Best Practices
- **Test user behavior, not implementation**
- **Arrange-Act-Assert** pattern
- **Mock external dependencies**
- **Test error states and edge cases**
- **Accessibility testing** included

## 🚀 Deployment & DevOps

### 1. Environment Strategy
- **Development**: Hot reload, detailed errors
- **Staging**: Production-like environment
- **Production**: Optimized builds, error monitoring

### 2. CI/CD Pipeline
```yaml
# .github/workflows/deploy.yml
name: Deploy to Production
on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
      - run: npm ci
      - run: npm run build
      - run: npm test

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to Vercel
        run: npx vercel --prod
```

### 3. Monitoring & Analytics
- **Vercel Analytics** for performance metrics
- **Sentry** for error tracking
- **LogRocket** for session replay
- **Core Web Vitals** monitoring

## 📝 Code Quality Standards

### 1. TypeScript Configuration
```json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "exactOptionalPropertyTypes": true
  }
}
```

### 2. ESLint Configuration
```json
{
  "extends": [
    "next/core-web-vitals",
    "@typescript-eslint/recommended",
    "prettier"
  ],
  "rules": {
    "@typescript-eslint/no-unused-vars": "error",
    "@typescript-eslint/explicit-function-return-type": "warn",
    "react-hooks/exhaustive-deps": "warn"
  }
}
```

### 3. Pre-commit Hooks
```json
{
  "husky": {
    "hooks": {
      "pre-commit": "lint-staged",
      "commit-msg": "commitlint -E HUSKY_GIT_PARAMS"
    }
  },
  "lint-staged": {
    "*.{ts,tsx}": ["eslint --fix", "prettier --write"],
    "*.{md,json}": ["prettier --write"]
  }
}
```

## 🔧 Development Workflow

### 1. Git Strategy
- **Feature branches** from `develop`
- **Squash merges** to `main`
- **Semantic versioning** for releases
- **Conventional commits** for changelog generation

### 2. Code Review Process
- **Automated checks**: Lint, test, type check
- **Peer review**: At least one approval required
- **QA validation**: Manual testing checklist
- **Security review**: For sensitive changes

### 3. Documentation
- **README.md** for project overview
- **API documentation** with OpenAPI/Swagger
- **Component documentation** with Storybook
- **Architecture diagrams** in docs/architecture/

## 🎯 Performance Targets

### Core Web Vitals
- **LCP (Largest Contentful Paint)**: < 2.5 seconds
- **FID (First Input Delay)**: < 100 milliseconds
- **CLS (Cumulative Layout Shift)**: < 0.1

### Bundle Size
- **First load**: < 100 KB gzipped
- **Subsequent loads**: < 50 KB gzipped
- **Vendor chunks**: Separated and cached

### Runtime Performance
- **Time to Interactive**: < 3 seconds
- **Memory usage**: < 50 MB average
- **Error rate**: < 0.1%

## 🚨 Error Handling

### 1. Error Boundaries
```tsx
class ErrorBoundary extends Component {
  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Log to error reporting service
    console.error('Error caught by boundary:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return <ErrorFallback error={this.state.error} />;
    }
    return this.props.children;
  }
}
```

### 2. API Error Handling
```tsx
export async function apiRequest<T>(url: string): Promise<T> {
  try {
    const response = await fetch(url);

    if (!response.ok) {
      throw new APIError(response.status, await response.text());
    }

    return response.json();
  } catch (error) {
    if (error instanceof APIError) {
      // Handle API errors
      throw error;
    }

    // Handle network errors
    throw new NetworkError('Failed to connect to server');
  }
}
```

### 3. User-Friendly Error Messages
- **Validation errors**: Clear, actionable messages
- **Network errors**: Retry options and offline support
- **Unexpected errors**: Generic fallback with error reporting

## 📚 Learning Resources

### Official Documentation
- [Next.js Documentation](https://nextjs.org/docs)
- [React Documentation](https://react.dev)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)

### Community Resources
- [Next.js GitHub Discussions](https://github.com/vercel/next.js/discussions)
- [Reactiflux Discord](https://www.reactiflux.com)
- [TypeScript Community Discord](https://discord.gg/typescript)

### Tools & Libraries
- [shadcn/ui](https://ui.shadcn.com) - Modern UI components
- [TanStack Query](https://tanstack.com/query) - Data fetching
- [Zustand](https://zustand-demo.pmnd.rs) - State management
- [React Hook Form](https://react-hook-form.com) - Form handling

---

*These guidelines evolve with Next.js and React ecosystem changes. Regular reviews ensure continued relevance and effectiveness.*