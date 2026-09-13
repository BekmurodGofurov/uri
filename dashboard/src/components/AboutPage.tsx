import React, { useState } from 'react';
import {
  Globe,
  ExternalLink,
  ArrowLeft,
  Sparkles,
  Users,
  Workflow,
  User,
} from 'lucide-react';
import { isModifiedClick } from '../utils/route';

interface AboutPageProps {
  onBack: () => void;
}

interface TeamMember {
  name: string;
  tag: string;
  about: string;
  image?: string;
  github?: string;
  linkedin?: string;
  website?: string;
}

const GithubIcon: React.FC<{ className?: string }> = ({ className = 'w-4 h-4' }) => (
  <svg
    className={className}
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <path d="M15 22v-4a4.8 4.8 0 0 0-1-3.5c3 0 6-2 6-5.5.08-1.25-.27-2.48-1-3.5.28-1.15.28-2.35 0-3.5 0 0-1 0-3 1.5-2.64-.5-5.36-.5-8 0C6 2 5 2 5 2c-.3 1.15-.3 2.35 0 3.5A5.403 5.403 0 0 0 4 9c0 3.5 3 5.5 6 5.5-.39.49-.68 1.05-.85 1.65-.17.6-.22 1.23-.15 1.85v4" />
    <path d="M9 18c-4.51 2-5-2-7-2" />
  </svg>
);

const LinkedinIcon: React.FC<{ className?: string }> = ({ className = 'w-4 h-4' }) => (
  <svg
    className={className}
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z" />
    <rect width="4" height="12" x="2" y="9" />
    <circle cx="4" cy="4" r="2" />
  </svg>
);


const TeamMemberCard: React.FC<{ member: TeamMember }> = ({ member }) => {
  const [imageError, setImageError] = useState(false);

  return (
    <div className="bg-white rounded-xl border border-slate-200/80 shadow-xs hover:shadow-md transition overflow-hidden flex flex-col h-full group">
      {/* Top: Image area */}
      {/* Top: Image area with natural aspect-[4/3] */}
      <div className="relative w-full aspect-[4/3] bg-gradient-to-br from-slate-100 to-slate-200 border-b border-slate-100 overflow-hidden flex items-center justify-center">
        {member.image && !imageError ? (
          <img
            src={member.image}
            alt={member.name}
            onError={() => setImageError(true)}
            className="w-full h-full object-cover group-hover:scale-105 transition duration-300"
          />
        ) : (
          <div className="flex flex-col items-center justify-center gap-1.5 text-slate-400 select-none">
            <div className="w-14 h-14 rounded-full bg-slate-200/80 flex items-center justify-center text-slate-600 font-bold text-lg shadow-inner">
              {member.name
                .split(' ')
                .map((n) => n[0])
                .join('')}
            </div>
            <span className="text-[11px] font-medium text-slate-400 flex items-center gap-1">
              <User className="w-3.5 h-3.5" />
              Photo
            </span>
          </div>
        )}
      </div>

      {/* Bottom Content Area */}
      <div className="p-3.5 sm:p-4 flex flex-col flex-1 justify-between gap-2.5 text-left">
        {/* Line 1: Name on the left, Tag on the right (Unified Styling, no ugly truncation) */}
        <div className="flex items-center justify-between gap-1.5">
          <h3 className="font-bold text-slate-900 text-sm sm:text-base leading-tight" title={member.name}>
            {member.name}
          </h3>
          <span className="px-2.5 py-0.5 rounded-full text-[10px] sm:text-xs font-semibold bg-uzum-50 text-uzum-700 border border-uzum-200 shrink-0">
            {member.tag}
          </span>
        </div>

        {/* Line 2: About / Description */}
        <p className="text-xs text-slate-600 leading-snug line-clamp-2" title={member.about}>
          {member.about}
        </p>

        {/* Line 3: Social & Portfolio Links */}
        <div className="flex items-center gap-1.5 pt-2 border-t border-slate-100">
          {member.github && (
            <a
              href={member.github}
              target="_blank"
              rel="noopener noreferrer"
              className="p-1.5 rounded-lg bg-slate-100 hover:bg-slate-900 text-slate-700 hover:text-white transition"
              title="GitHub"
            >
              <GithubIcon className="w-3.5 h-3.5" />
            </a>
          )}
          {member.linkedin && (
            <a
              href={member.linkedin}
              target="_blank"
              rel="noopener noreferrer"
              className="p-1.5 rounded-lg bg-slate-100 hover:bg-[#0077B5] text-slate-700 hover:text-white transition"
              title="LinkedIn"
            >
              <LinkedinIcon className="w-3.5 h-3.5" />
            </a>
          )}
          {member.website && (
            <a
              href={member.website}
              target="_blank"
              rel="noopener noreferrer"
              className="p-1.5 rounded-lg bg-slate-100 hover:bg-uzum-600 text-slate-700 hover:text-white transition"
              title="Website / Portfolio"
            >
              <Globe className="w-3.5 h-3.5" />
            </a>
          )}
        </div>
      </div>
    </div>
  );
};

export const AboutPage: React.FC<AboutPageProps> = ({ onBack }) => {
  const handleBackClick = (e: React.MouseEvent<HTMLAnchorElement>) => {
    if (isModifiedClick(e)) return;
    e.preventDefault();
    onBack();
  };

  // Row 1: Leader card (Exact same width as row 2 cards)
  const leader: TeamMember = {
    name: 'Nodirbek Vositov',
    tag: 'Team Lead',
    about: 'Strategic direction, project coordination, architecture governance, and overall leadership across the platform lifecycle.',
    image: 'https://media.licdn.com/dms/image/v2/D4D03AQFC7HUcKT1MjA/profile-displayphoto-crop_800_800/B4DZfP71iYGUAI-/0/1751540259625?e=1790812800&v=beta&t=avMaGCiFFmxrVZS27sX2WNdfZSSVFrlROxm0NGpsasc',
    github: 'https://github.com/Nodirbek-py',
    linkedin: 'https://www.linkedin.com/in/nodirbekvositov',
    // website: 'https://vositov.uz',
  };

  // Row 2: 3 Engineering members (2 ML, 1 Backend)
  const members: TeamMember[] = [
    {
      name: 'Hayotbek',
      tag: 'ML Engineer',
      about: 'Uzbek text preprocessing, morphological tokenization, sentiment classification modeling, TF-IDF baseline and transformer benchmarking.',
      image: 'https://media.licdn.com/dms/image/v2/D4D35AQH6L_OHsag3Qg/profile-framedphoto-shrink_800_800/B4DZ37cafcGcAg-/0/1778040023307?e=1789905600&v=beta&t=lnO3t0b_7pfqvBrxIPm_-F4dlUgZ2hIek7kagT8P69w',
      github: 'https://github.com/HayotbekDeveloper',
      linkedin: 'https://www.linkedin.com/in/muhammadayub-jamolov-a26270309/',
      website: 'https://taplink.cc/hcc_uz',
    },
    {
      name: 'Biloliddin Isomiddinov',
      tag: 'ML Engineer',
      about: 'Aspect-based sentiment analysis (ABSA) multi-label taxonomy, training dataset expansion, and 300-sample Gold standard benchmark set.',
      image: 'https://avatars.githubusercontent.com/u/203096650?v=4',
      github: 'https://github.com/Biloliddin177',
      linkedin: 'https://www.linkedin.com/in/biloliddin-isomiddinov/',
      website: 'https://isomiddinov.vercel.app',
    },
    {
      name: 'Bekmurod G\'ofurov',
      tag: 'Backend Engineer',
      about: 'Microservices architecture, FastAPI Gateway, PostgreSQL database layer, Ingest pipeline, Model Registry, and React analytics dashboard.',
      image: 'https://avatars.githubusercontent.com/u/128789196?v=4',
      github: 'https://github.com/BekmurodGofurov',
      linkedin: 'https://www.linkedin.com/in/bekmurod-gofurov',
      website: 'https://bekmurod.uz',
    },
  ];

  return (
    <div className="space-y-8 sm:space-y-12">
      {/* SCREEN 1: Overview & How It Works (Full screen below fixed header; Team Members is hidden) */}
      <section className="min-h-[calc(100vh-6rem)] flex flex-col justify-between max-w-5xl mx-auto text-center py-4">
        {/* Navigation breadcrumb */}
        <div className="text-left w-full">
          <a
            href="/"
            onClick={handleBackClick}
            className="inline-flex items-center gap-2 text-xs font-semibold text-slate-500 hover:text-uzum-600 transition"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Back to Catalog</span>
          </a>
        </div>

        {/* Overview & How It Works Content */}
        <div className="my-auto space-y-8 sm:space-y-10 py-6">
          {/* Project Overview */}
          <div className="space-y-3 max-w-4xl mx-auto">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-uzum-50 text-uzum-700">
              <Sparkles className="w-3.5 h-3.5 text-uzum-600" />
              <span>Project Overview</span>
            </div>

            <h1 className="text-3xl sm:text-4xl lg:text-5xl font-black text-slate-900 tracking-tight leading-tight">
              Uzum Review Intelligence
            </h1>

            <p className="text-sm sm:text-base lg:text-lg text-slate-600 leading-relaxed">
              E-commerce marketplaces like Uzum Market receive thousands of customer reviews every week.
              Manually reading each review is practically impossible, and basic star ratings often mask critical product defects,
              damaged packaging, or delayed deliveries. Uzum Review Intelligence (URI) is an end-to-end Machine Learning platform
              tailored for the Uzbek language that automatically analyzes customer feedback, classifies sentiment,
              and uncovers actionable operational insights in real time.
            </p>
          </div>

          {/* How It Works */}
          <div className="space-y-3 max-w-4xl mx-auto">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-uzum-50 text-uzum-700">
              <Workflow className="w-3.5 h-3.5 text-uzum-600" />
              <span>How It Works</span>
            </div>

            <h2 className="text-xl sm:text-2xl lg:text-3xl font-extrabold text-slate-900 tracking-tight">
              How The System Works
            </h2>

            <p className="text-xs sm:text-sm lg:text-base text-slate-600 leading-relaxed">
              The platform processes real customer reviews from Uzum Market—trained and evaluated on public datasets such as{' '}
              <a
                href="https://huggingface.co/datasets/risqaliyevds/uzbek-sentiment-analysis"
                target="_blank"
                rel="noopener noreferrer"
                className="font-semibold text-uzum-600 hover:text-uzum-700 underline underline-offset-4 inline-flex items-center gap-0.5"
              >
                risqaliyevds/uzbek-sentiment-analysis
                <ExternalLink className="w-3 h-3" />
              </a>{' '}
              (352,000+ reviews),{' '}
              <a
                href="https://huggingface.co/datasets/Sanatbek/aspect-based-sentiment-analysis-uzbek"
                target="_blank"
                rel="noopener noreferrer"
                className="font-semibold text-uzum-600 hover:text-uzum-700 underline underline-offset-4 inline-flex items-center gap-0.5"
              >
                Sanatbek/aspect-based-sentiment-analysis-uzbek
                <ExternalLink className="w-3 h-3" />
              </a>, and benchmarked against{' '}
              <a
                href="https://github.com/sssplash6/uzbek-sentiment-analysis"
                target="_blank"
                rel="noopener noreferrer"
                className="font-semibold text-uzum-600 hover:text-uzum-700 underline underline-offset-4 inline-flex items-center gap-0.5"
              >
                sssplash6 research
                <ExternalLink className="w-3 h-3" />
              </a>.
              It cleans and standardizes Uzbek Latin text and apostrophes, classifies overall sentiment as positive, neutral, or negative,
              and identifies specific operational aspects including delivery, product quality, price, seller responsiveness, and packaging.
              All predictions and analytical metrics are persisted in a database and presented interactively across this dashboard.
            </p>
          </div>
        </div>

        {/* Scroll hint to Team Members */}
        <div className="text-center pt-2 pb-2">
          <a
            href="#team-members"
            onClick={(e) => {
              e.preventDefault();
              document.getElementById('team-members')?.scrollIntoView({ behavior: 'smooth' });
            }}
            className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-400 hover:text-uzum-600 transition group cursor-pointer"
          >
            <span>Team Members</span>
            <span className="group-hover:translate-y-0.5 transition-transform">↓</span>
          </a>
        </div>
      </section>

      {/* SCREEN 2: Team Members Section (Full 100vh screen; both rows fit completely) */}
      <section
        id="team-members"
        className="min-h-screen flex flex-col justify-center max-w-5xl mx-auto py-6 sm:py-8"
      >
        <div className="text-center space-y-1.5 max-w-xl mx-auto mb-4 sm:mb-5">
          <div className="inline-flex items-center gap-1.5 px-3 py-0.5 rounded-full text-xs font-semibold bg-uzum-50 text-uzum-700">
            <Users className="w-3.5 h-3.5 text-uzum-600" />
            <span>Contributors</span>
          </div>
          <h2 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight">
            Team Members
          </h2>
          <p className="text-xs sm:text-sm text-slate-500">
            The engineering and platform team behind Uzum Review Intelligence.
          </p>
        </div>

        {/* Row 1: Nodirbek Vositov (Centered, EXACT SAME CARD WIDTH as row 2) */}
        <div className="flex justify-center mb-4 sm:mb-5">
          <div className="w-full max-w-[265px] sm:max-w-[275px]">
            <TeamMemberCard member={leader} />
          </div>
        </div>

        {/* Row 2: 3 Engineering Members (ML 1, ML 2, Backend - EXACT SAME CARD WIDTH) */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 sm:gap-6 justify-items-center max-w-4xl mx-auto w-full">
          {members.map((member) => (
            <div key={member.name} className="w-full max-w-[265px] sm:max-w-[275px]">
              <TeamMemberCard member={member} />
            </div>
          ))}
        </div>
      </section>
    </div>
  );
};
