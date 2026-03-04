import React, { useState } from 'react';
import { Search, Scale, Gavel, BookOpen, Shield, ChevronRight, MessageSquare } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const App = () => {
    const [searchQuery, setSearchQuery] = useState('');
    const [isSearching, setIsSearching] = useState(false);

    const handleSearch = (e) => {
        e.preventDefault();
        setIsSearching(true);
        // Simulate API call
        setTimeout(() => setIsSearching(false), 2000);
    };

    return (
        <div className="min-h-screen hero-gradient">
            {/* Navigation */}
            <nav className="flex items-center justify-between px-8 py-6 border-b border-slate-200/50 backdrop-blur-sm sticky top-0 z-50">
                <div className="flex items-center gap-2 group cursor-pointer">
                    <div className="bg-legal-900 p-2 rounded-lg text-gold-500 group-hover:rotate-12 transition-transform duration-300">
                        <Scale size={24} />
                    </div>
                    <span className="text-2xl font-playfair font-bold text-legal-900 tracking-tight">INDIA LEGAL <span className="text-gold-500">AI</span></span>
                </div>

                <div className="hidden md:flex items-center gap-8 text-legal-700 font-medium font-outfit">
                    <a href="#" className="hover:text-gold-600 transition-colors">Judgments</a>
                    <a href="#" className="hover:text-gold-600 transition-colors">AI Analysis</a>
                    <a href="#" className="hover:text-gold-600 transition-colors">Resources</a>
                    <button className="btn btn-primary text-sm">Sign In</button>
                </div>
            </nav>

            {/* Hero Section */}
            <header className="max-w-7xl mx-auto px-6 pt-24 pb-16 text-center">
                <motion.div
                    initial={{ opacity: 0, y: 30 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8 }}
                >
                    <span className="inline-block px-4 py-1.5 mb-6 text-xs font-bold tracking-widest text-gold-600 uppercase bg-gold-500/10 rounded-full border border-gold-500/20">
                        Intelligent Legal Search redefined
                    </span>
                    <h1 className="text-5xl md:text-7xl font-playfair font-bold text-legal-900 mb-8 leading-[1.1]">
                        Empowering Justice through <br />
                        <span className="text-gold-600 italic">Conversational Intelligence</span>
                    </h1>
                    <p className="max-w-2xl mx-auto text-lg text-slate-600 mb-12 font-outfit leading-relaxed">
                        Instantly surface relevant Indian judgments, extract key principles, and navigate complex legal datasets with our enterprise-grade AI engine.
                    </p>

                    {/* Search Bar */}
                    <form
                        onSubmit={handleSearch}
                        className="max-w-3xl mx-auto relative group"
                    >
                        <div className="absolute -inset-1 bg-gradient-to-r from-gold-500 to-legal-900 rounded-2xl blur opacity-25 group-hover:opacity-40 transition duration-1000 group-hover:duration-200"></div>
                        <div className="relative flex items-center bg-white p-2 rounded-xl border border-slate-200 shadow-2xl">
                            <Search className="ml-4 text-slate-400" size={24} />
                            <input
                                type="text"
                                placeholder="Search judgments by citation, party, or legal concept..."
                                className="w-full px-4 py-4 focus:outline-none text-slate-700 font-outfit text-lg"
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                            />
                            <button
                                type="submit"
                                className="btn btn-primary h-14 px-8 whitespace-nowrap"
                            >
                                {isSearching ? 'Processing...' : 'Search Judgment'}
                            </button>
                        </div>
                    </form>
                </motion.div>
            </header>

            {/* Features Grid */}
            <section className="max-w-7xl mx-auto px-6 py-20">
                <div className="grid md:grid-cols-3 gap-8">
                    {[
                        { icon: <Gavel />, title: "Precision Retrieval", desc: "Semantic search that understands the intent behind your query, not just keywords." },
                        { icon: <BookOpen />, title: "Live Synthesis", desc: "Summarize thousands of pages of legal text into concise, actionable briefs in seconds." },
                        { icon: <Shield />, title: "Verified Data", desc: "Direct citations to official court records ensuring absolute accuracy for your research." }
                    ].map((feature, i) => (
                        <motion.div
                            key={i}
                            whileHover={{ y: -5 }}
                            className="p-8 rounded-2xl card-glass border-slate-200 transition-all duration-300"
                        >
                            <div className="w-12 h-12 bg-legal-900 text-gold-500 rounded-xl flex items-center justify-center mb-6">
                                {feature.icon}
                            </div>
                            <h3 className="text-xl font-bold text-legal-900 mb-3 font-playfair">{feature.title}</h3>
                            <p className="text-slate-600 leading-relaxed text-sm">
                                {feature.desc}
                            </p>
                        </motion.div>
                    ))}
                </div>
            </section>

            {/* Bottom CTA */}
            <footer className="bg-legal-900 text-white py-16 mt-20 relative overflow-hidden">
                <div className="max-w-7xl mx-auto px-6 relative z-10 flex flex-col md:flex-row justify-between items-center gap-12">
                    <div className="max-w-xl text-center md:text-left">
                        <h2 className="text-3xl font-playfair font-bold mb-4">Ready to accelerate your legal research?</h2>
                        <p className="text-slate-400">Join elite advocates across India using modern AI to win more cases.</p>
                    </div>
                    <button className="btn bg-gold-500 text-legal-900 hover:bg-gold-600 font-bold px-10 py-4 text-lg animate-float">
                        Get Project Access <ChevronRight />
                    </button>
                </div>
                {/* Background Accents */}
                <div className="absolute top-0 right-0 w-64 h-64 bg-gold-500/10 blur-[100px] rounded-full -mr-32 -mt-32"></div>
            </footer building>
        </div>
    );
};

export default App;
