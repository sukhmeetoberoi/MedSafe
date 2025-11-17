# MedSummarize Frontend

A modern, professional website for MedSummarize - an AI-powered medical report summarization system.

## 🚀 Features

- **Modern UI/UX**: Built with React, Tailwind CSS, and Framer Motion
- **Responsive Design**: Optimized for desktop, tablet, and mobile devices
- **Interactive Components**: Smooth animations and transitions
- **Professional Medical Theme**: Clean, trustworthy design with medical color palette
- **Accessibility**: WCAG 2.1 AA compliant
- **SEO Optimized**: Meta tags and semantic HTML

## 🛠 Technology Stack

- **Frontend Framework**: React 18+ with hooks
- **Build Tool**: Vite for fast development and optimized builds
- **Styling**: Tailwind CSS with custom medical theme
- **Animations**: Framer Motion for smooth interactions
- **Icons**: Lucide React for consistent iconography
- **Forms**: React Hook Form for form handling
- **File Upload**: React Dropzone with progress indicators

## 📦 Installation

1. Clone the repository:
```bash
git clone https://github.com/your-org/medsafe.git
cd medsafe/frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create environment variables:
```bash
cp .env.example .env
```

4. Start the development server:
```bash
npm run dev
```

## 🏗 Project Structure

```
frontend/
├── public/                 # Static assets
├── src/
│   ├── components/         # Reusable UI components
│   │   ├── layout/        # Header, Footer, Navigation
│   │   ├── sections/      # Page sections (Hero, About, Features, etc.)
│   │   ├── ui/           # Generic UI components
│   │   ├── upload/       # File upload components
│   │   ├── results/      # Results display components
│   │   └── forms/        # Form components
│   ├── hooks/            # Custom React hooks
│   ├── utils/            # Utility functions
│   ├── styles/           # Global styles and themes
│   └── assets/           # Images, icons, fonts
├── package.json
├── vite.config.js
├── tailwind.config.js
└── README.md
```

## 🎨 Design System

### Color Palette
- **Primary**: #007acc (Medical Blue)
- **Secondary**: #00a8cc (Teal Accent)
- **Background**: #f0f8ff (Light Blue Background)
- **Text**: #2c3e50 (Dark Blue-Gray)
- **Alert**: #e74c3c (Alert Red)
- **Neutral**: #ffffff (White), #f8fafb (Light Gray)

### Typography
- **Headings**: Inter font, bold weights
- **Body**: Inter font, regular weights
- **Hierarchy**: Clear contrast between headings and body text

### Components
- **Buttons**: Primary (blue), Secondary (teal), with hover states
- **Cards**: White backgrounds with subtle shadows
- **Forms**: Clean input fields with focus states
- **Navigation**: Smooth scroll with active state highlighting

## 📱 Responsive Design

- **Mobile**: 320px - 768px (stacked layout, hamburger menu)
- **Tablet**: 768px - 1024px (adapted grid, touch-friendly)
- **Desktop**: 1024px+ (full layout, hover interactions)

## ⚡ Performance

- **Page Load**: <3 seconds on 3G networks
- **Animations**: 60fps smooth transitions
- **Bundle Size**: Optimized with code splitting
- **Images**: Lazy loading for better performance

## 🔧 Development Scripts

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run linter
npm run lint
```

## 🚀 Deployment

### Vercel (Recommended)
1. Connect your repository to Vercel
2. Set environment variables in Vercel dashboard
3. Deploy automatically on push to main branch

### Netlify
1. Connect your repository to Netlify
2. Configure build settings: `npm run build`
3. Set environment variables in Netlify dashboard

### Static Hosting
```bash
npm run build
# Deploy the `dist` folder to any static hosting service
```

## 🔒 Security

- **Environment Variables**: Sensitive data stored in .env files
- **Content Security Policy**: Configured for production
- **HTTPS**: Enforced in production
- **Input Validation**: Form inputs validated and sanitized

## 📊 Analytics & Monitoring

- **Google Analytics**: Page views and user behavior
- **Performance Monitoring**: Core Web Vitals tracking
- **Error Reporting**: Automatic error capture and reporting

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support, please contact:
- Email: support@medsummarize.com
- GitHub Issues: Create an issue in the repository
- Documentation: Check the project wiki

## 🔄 Version History

- **v1.0.0**: Initial release with all core features
- Responsive design and mobile optimization
- Interactive demo section
- Contact form with validation
- Professional medical theme

## 🌟 Features Coming Soon

- User authentication system
- File upload with progress tracking
- Real-time AI processing
- Interactive Q&A interface
- Multilingual support
- Dark mode theme