import React from 'react';
import { motion } from 'framer-motion';
import { Clock, Users, Shield, Award, TrendingUp, CheckCircle } from 'lucide-react';
const WhyChoose = () => {
  const benefits = [
    {
      icon: Clock,
      title: 'Saves Doctors\' Time',
      description: 'Reduce report review time by 80% while maintaining clinical accuracy and attention to detail.',
      stats: ['80% faster review', '2 hours saved per day', '50+ more patients seen'],
      color: 'bg-blue-500',
      bgColor: 'bg-blue-50'
    },
    {
      icon: Users,
      title: 'Improves Patient Understanding',
      description: 'Transform complex medical jargon into clear, actionable insights that patients can easily comprehend.',
      stats: ['95% patient comprehension', '40% fewer follow-up calls', 'Better health outcomes'],
      color: 'bg-green-500',
      bgColor: 'bg-green-50'
    },
    {
      icon: Shield,
      title: 'Privacy-Focused',
      description: 'HIPAA and GDPR compliant with end-to-end encryption and automatic PHI redaction.',
      stats: ['HIPAA compliant', '256-bit encryption', 'Zero data retention risk'],
      color: 'bg-purple-500',
      bgColor: 'bg-purple-50'
    },
    {
      icon: Award,
      title: 'Accurate & Medically Aligned',
      description: 'Validated by healthcare professionals with 99% accuracy in medical information extraction.',
      stats: ['99% accuracy rate', 'Peer-reviewed algorithms', 'Regular medical validation'],
      color: 'bg-yellow-500',
      bgColor: 'bg-yellow-50'
    }
  ];

  const testimonials = [
    {
      quote: "MedSummarize has revolutionized how I review patient reports. What used to take hours now takes minutes.",
      author: "Dr. Sarah Johnson",
      title: "Cardiologist",
      clinic: "Mayo Clinic"
    },
    {
      quote: "Finally, I can understand my medical reports without calling my doctor for every question.",
      author: "Michael Chen",
      title: "Patient",
      clinic: "San Francisco, CA"
    },
    {
      quote: "The accuracy is remarkable. It catches details I might miss in a quick scan of lengthy reports.",
      author: "Dr. Emily Rodriguez",
      title: "Radiologist",
      clinic: "Cleveland Clinic"
    }
  ];

  const comparisonData = [
    { feature: 'Manual Review', time: '2-4 hours', accuracy: '85%', cost: '$200/report' },
    { feature: 'MedSummarize', time: '<2 minutes', accuracy: '99%', cost: '$5/report' }
  ];

  return (
    <section id="why-choose" className="py-20 bg-light-gradient-bg">
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
            Why Choose MedSummarize
          </motion.h2>
          <motion.p
            className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            viewport={{ once: true }}
          >
            Discover why thousands of healthcare professionals and patients trust MedSummarize for accurate, secure, and instant medical report analysis.
          </motion.p>
        </motion.div>

        {/* Main Benefits Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mb-20">
          {benefits.map((benefit, index) => (
            <motion.div
              key={benefit.title}
              className="group"
              initial={{ opacity: 0, y: 50 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.1 * index }}
              viewport={{ once: true }}
              whileHover={{ y: -10 }}
            >
              <div className="card h-full border-0 hover:shadow-2xl transition-all duration-300">
                {/* Icon */}
                <motion.div
                  className={`w-20 h-20 mx-auto mb-6 rounded-full ${benefit.color} text-white flex items-center justify-center group-hover:scale-110 transition-transform duration-300`}
                  whileHover={{ rotate: 360 }}
                  transition={{ duration: 0.6 }}
                >
                  <benefit.icon className="w-10 h-10" />
                </motion.div>

                {/* Content */}
                <div className="text-center">
                  <h3 className="text-xl font-semibold text-dark-blue-gray mb-4 group-hover:text-medical-blue transition-colors duration-300">
                    {benefit.title}
                  </h3>
                  <p className="text-gray-600 mb-6 leading-relaxed">
                    {benefit.description}
                  </p>

                  {/* Stats */}
                  <div className={`${benefit.bgColor} rounded-lg p-4 space-y-2`}>
                    {benefit.stats.map((stat, statIndex) => (
                      <motion.div
                        key={stat}
                        className="flex items-center justify-center space-x-2"
                        initial={{ opacity: 0, x: -10 }}
                        whileInView={{ opacity: 1, x: 0 }}
                        transition={{ duration: 0.4, delay: 0.1 * statIndex }}
                        viewport={{ once: true }}
                      >
                        <CheckCircle className="w-4 h-4 text-green-500 flex-shrink-0" />
                        <span className="text-sm font-medium text-gray-700">{stat}</span>
                      </motion.div>
                    ))}
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Comparison Section */}
        <motion.div
          className="mb-20"
          initial={{ opacity: 0, scale: 0.9 }}
          whileInView={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
        >
          <h3 className="text-3xl font-bold text-center text-dark-blue-gray mb-12">
            Traditional vs. AI-Powered Analysis
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {comparisonData.map((method, index) => (
              <motion.div
                key={method.feature}
                className={`relative overflow-hidden rounded-2xl p-8 ${method.feature === 'MedSummarize'
                  ? 'bg-gradient-to-br from-medical-blue to-teal-accent text-white'
                  : 'bg-white border-2 border-gray-200'
                  }`}
                initial={{ opacity: 0, x: index === 0 ? -50 : 50 }}
                whileInView={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.6, delay: 0.1 * index }}
                viewport={{ once: true }}
                whileHover={{ scale: 1.05 }}
              >
                {method.feature === 'MedSummarize' && (
                  <div className="absolute top-4 right-4 bg-white/20 backdrop-blur-sm px-3 py-1 rounded-full text-sm font-semibold">
                    RECOMMENDED
                  </div>
                )}

                <h4 className={`text-2xl font-bold mb-6 ${method.feature === 'MedSummarize' ? 'text-white' : 'text-dark-blue-gray'
                  }`}>
                  {method.feature}
                </h4>

                <div className="space-y-4">
                  {[
                    { label: 'Processing Time', value: method.time },
                    { label: 'Accuracy Rate', value: method.accuracy },
                    { label: 'Cost per Report', value: method.cost }
                  ].map((item) => (
                    <div key={item.label} className="flex justify-between items-center">
                      <span className={`${method.feature === 'MedSummarize' ? 'text-blue-100' : 'text-gray-600'
                        }`}>
                        {item.label}
                      </span>
                      <span className={`font-bold ${method.feature === 'MedSummarize' ? 'text-white' : 'text-dark-blue-gray'
                        }`}>
                        {item.value}
                      </span>
                    </div>
                  ))}
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* ROI Calculator */}
        <motion.div
          className="bg-white rounded-2xl shadow-xl p-8 md:p-12 mb-20"
          initial={{ opacity: 0, y: 50 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
        >
          <h3 className="text-2xl md:text-3xl font-bold text-center text-dark-blue-gray mb-8">
            Return on Investment
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-center">
            {[
              { metric: 'Time Saved', value: '16 hours/week', description: 'Per healthcare provider' },
              { metric: 'Cost Reduction', value: '75%', description: 'Compared to manual review' },
              { metric: 'ROI', value: '1200%', description: 'Within first 6 months' }
            ].map((item, index) => (
              <motion.div
                key={item.metric}
                className="p-6"
                initial={{ opacity: 0, scale: 0.8 }}
                whileInView={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.6, delay: 0.1 * index }}
                viewport={{ once: true }}
              >
                <div className="text-3xl font-bold text-medical-blue mb-2">{item.value}</div>
                <div className="font-semibold text-dark-blue-gray mb-1">{item.metric}</div>
                <div className="text-sm text-gray-600">{item.description}</div>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Testimonials */}
        <motion.div
          className="mb-16"
          initial={{ opacity: 0, y: 50 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
        >
          <h3 className="text-3xl font-bold text-center text-dark-blue-gray mb-12">
            What Our Users Say
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {testimonials.map((testimonial, index) => (
              <motion.div
                key={testimonial.author}
                className="card"
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.1 * index }}
                viewport={{ once: true }}
                whileHover={{ scale: 1.05 }}
              >
                <div className="mb-4">
                  <div className="flex text-yellow-400 mb-4">
                    {[...Array(5)].map((_, i) => (
                      <span key={i}>⭐</span>
                    ))}
                  </div>
                  <p className="text-gray-600 italic leading-relaxed">
                    "{testimonial.quote}"
                  </p>
                </div>
                <div className="border-t pt-4">
                  <div className="font-semibold text-dark-blue-gray">{testimonial.author}</div>
                  <div className="text-sm text-gray-500">{testimonial.title}</div>
                  <div className="text-sm text-gray-400">{testimonial.clinic}</div>
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Call to Action */}
        <motion.div
          className="text-center"
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
        >
          <div className="bg-gradient-to-r from-medical-blue to-teal-accent rounded-2xl p-8 md:p-12 text-white">
            <h3 className="text-2xl md:text-3xl font-bold mb-4">
              Ready to Transform Your Medical Report Analysis?
            </h3>
            <p className="text-blue-100 mb-8 max-w-2xl mx-auto text-lg">
              Join thousands of healthcare professionals who are already saving time, improving accuracy, and enhancing patient care with MedSummarize.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <motion.button
                className="bg-white text-medical-blue font-semibold py-3 px-8 rounded-lg hover:bg-gray-100 transition-colors duration-300"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                Start Free Trial
              </motion.button>
              <motion.button
                className="border-2 border-white text-white font-semibold py-3 px-8 rounded-lg hover:bg-white hover:text-medical-blue transition-all duration-300"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                Request Demo
              </motion.button>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
};

export default WhyChoose;