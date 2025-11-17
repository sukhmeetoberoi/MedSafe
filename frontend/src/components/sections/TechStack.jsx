import React from 'react';
import { motion } from 'framer-motion';
import { Cpu, Database, Globe, Shield, Cloud, Code } from 'lucide-react';

const TechStack = () => {
  const techCategories = [
    {
      icon: Cpu,
      title: 'AI & Machine Learning',
      color: 'bg-gradient-to-br from-blue-500 to-purple-600',
      technologies: [
        { name: 'TensorFlow', description: 'Deep learning framework' },
        { name: 'PyTorch', description: 'Neural network library' },
        { name: 'spaCy', description: 'Natural language processing' },
        { name: 'Transformers', description: 'Pre-trained language models' },
        { name: 'LangChain', description: 'LLM application framework' }
      ]
    },
    {
      icon: Globe,
      title: 'Language Models',
      color: 'bg-gradient-to-br from-green-500 to-teal-600',
      technologies: [
        { name: 'Google Gemini Pro', description: 'Advanced multimodal AI' },
        { name: 'GPT-4', description: 'Language understanding' },
        { name: 'BERT', description: 'Text embeddings' },
        { name: 'T5', description: 'Text-to-text transfer' },
        { name: 'Medical BERT', description: 'Healthcare-specific models' }
      ]
    },
    {
      icon: Database,
      title: 'Data & Storage',
      color: 'bg-gradient-to-br from-orange-500 to-red-600',
      technologies: [
        { name: 'MongoDB', description: 'Document database' },
        { name: 'PostgreSQL', description: 'Relational database' },
        { name: 'Pinecone', description: 'Vector database' },
        { name: 'Redis', description: 'In-memory caching' },
        { name: 'AWS S3', description: 'Object storage' }
      ]
    },
    {
      icon: Code,
      title: 'Backend Technologies',
      color: 'bg-gradient-to-br from-indigo-500 to-purple-600',
      technologies: [
        { name: 'Python', description: 'Core programming language' },
        { name: 'Flask', description: 'Lightweight web framework' },
        { name: 'Django', description: 'Full-stack framework' },
        { name: 'FastAPI', description: 'High-performance API' },
        { name: 'Celery', description: 'Task queue management' }
      ]
    },
    {
      icon: Cloud,
      title: 'Cloud & DevOps',
      color: 'bg-gradient-to-br from-cyan-500 to-blue-600',
      technologies: [
        { name: 'AWS', description: 'Cloud infrastructure' },
        { name: 'Vercel', description: 'Frontend deployment' },
        { name: 'Docker', description: 'Containerization' },
        { name: 'GitHub Actions', description: 'CI/CD pipeline' },
        { name: 'Kubernetes', description: 'Container orchestration' }
      ]
    },
    {
      icon: Shield,
      title: 'Security & Compliance',
      color: 'bg-gradient-to-br from-red-500 to-pink-600',
      technologies: [
        { name: 'Presidio', description: 'PHI detection & redaction' },
        { name: 'HashiCorp Vault', description: 'Secrets management' },
        { name: 'SSL/TLS', description: 'Data encryption' },
        { name: 'OAuth 2.0', description: 'Authentication' },
        { name: 'HIPAA Toolkit', description: 'Compliance automation' }
      ]
    }
  ];

  return (
    <section id="tech-stack" className="py-20 bg-white">
      <div className="container mx-auto px-4">
        {/* Section Header */}
        <motion.div
          className="text-center mb-16"
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
        >
          <motion.h2
            className="text-4xl md:text-5xl font-bold text-dark-blue-gray mb-6"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
            viewport={{ once: true }}
          >
            Technology Stack
          </motion.h2>
          <motion.p
            className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            viewport={{ once: true }}
          >
            Built with cutting-edge technologies to ensure accuracy, security, and scalability.
            Our stack combines the best of AI/ML, cloud infrastructure, and security frameworks.
          </motion.p>
        </motion.div>

        {/* Tech Categories Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-16">
          {techCategories.map((category, index) => (
            <motion.div
              key={category.title}
              className="group"
              initial={{ opacity: 0, y: 50 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.1 * index }}
              viewport={{ once: true }}
              whileHover={{ y: -10 }}
            >
              <div className="card h-full overflow-hidden">
                {/* Header */}
                <div className={`${category.color} p-6 text-white`}>
                  <motion.div
                    className="w-16 h-16 bg-white/20 rounded-full flex items-center justify-center mb-4 backdrop-blur-sm group-hover:scale-110 transition-transform duration-300"
                    whileHover={{ rotate: 360 }}
                    transition={{ duration: 0.6 }}
                  >
                    <category.icon className="w-8 h-8" />
                  </motion.div>
                  <h3 className="text-xl font-bold">{category.title}</h3>
                </div>

                {/* Technologies List */}
                <div className="p-6">
                  <div className="space-y-4">
                    {category.technologies.map((tech, techIndex) => (
                      <motion.div
                        key={tech.name}
                        className="flex items-start space-x-3 p-3 rounded-lg hover:bg-gray-50 transition-colors duration-200"
                        initial={{ opacity: 0, x: -20 }}
                        whileInView={{ opacity: 1, x: 0 }}
                        transition={{ duration: 0.4, delay: 0.05 * techIndex }}
                        viewport={{ once: true }}
                        whileHover={{ x: 5 }}
                      >
                        <div className="w-2 h-2 bg-teal-accent rounded-full mt-2 flex-shrink-0"></div>
                        <div className="flex-1">
                          <h4 className="font-semibold text-dark-blue-gray group-hover:text-medical-blue transition-colors duration-200">
                            {tech.name}
                          </h4>
                          <p className="text-sm text-gray-600">{tech.description}</p>
                        </div>
                      </motion.div>
                    ))}
                  </div>
                </div>

                {/* Hover Effect */}
                <div className="absolute inset-0 bg-gradient-to-br from-medical-blue/5 to-teal-accent/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none"></div>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Architecture Overview */}
        <motion.div
          className="bg-light-gradient-bg rounded-2xl p-8 md:p-12"
          initial={{ opacity: 0, scale: 0.9 }}
          whileInView={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
        >
          <h3 className="text-2xl md:text-3xl font-bold text-dark-blue-gray text-center mb-8">
            System Architecture
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              { layer: 'Frontend', tech: 'React, Tailwind CSS, Framer Motion', icon: '🎨' },
              { layer: 'API Gateway', tech: 'RESTful APIs, GraphQL, WebSockets', icon: '🌐' },
              { layer: 'Processing', tech: 'AI/ML Pipeline, Microservices', icon: '⚡' },
              { layer: 'Data Layer', tech: 'Vector DB, SQL, NoSQL, Cache', icon: '🗄️' }
            ].map((layer, index) => (
              <motion.div
                key={layer.layer}
                className="bg-white rounded-xl p-6 text-center shadow-md hover:shadow-lg transition-all duration-300"
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.1 * index }}
                viewport={{ once: true }}
                whileHover={{ y: -5 }}
              >
                <div className="text-4xl mb-4">{layer.icon}</div>
                <h4 className="font-semibold text-dark-blue-gray mb-2">{layer.layer}</h4>
                <p className="text-sm text-gray-600">{layer.tech}</p>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Performance Metrics */}
        <motion.div
          className="mt-16 grid grid-cols-2 md:grid-cols-4 gap-8"
          initial={{ opacity: 0, y: 50 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
        >
          {[
            ['<500ms', 'API Response'],
            ['99.9%', 'Uptime SLA'],
            ['10M+', 'API Calls/day'],
            ['24/7', 'Monitoring']
          ].map(([value, label], index) => (
            <motion.div
              key={value}
              className="text-center group"
              initial={{ opacity: 0, scale: 0.8 }}
              whileInView={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.6, delay: 0.1 * index }}
              viewport={{ once: true }}
            >
              <div className="w-20 h-20 mx-auto mb-4 bg-gradient-to-br from-medical-blue to-teal-accent rounded-full flex items-center justify-center text-white font-bold text-xl shadow-lg group-hover:scale-110 transition-transform duration-300">
                {value}
              </div>
              <div className="text-sm text-gray-600 font-medium">{label}</div>
            </motion.div>
          ))}
        </motion.div>

        {/* Security Badge */}
        <motion.div
          className="mt-16 text-center"
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
        >
          <div className="inline-flex items-center space-x-3 bg-green-50 border border-green-200 rounded-full px-6 py-3">
            <Shield className="w-5 h-5 text-green-600" />
            <span className="text-green-800 font-semibold">Enterprise-Grade Security & HIPAA Compliant</span>
          </div>
        </motion.div>
      </div>
    </section>
  );
};

export default TechStack;