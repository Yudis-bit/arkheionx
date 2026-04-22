'use client';

import { motion } from 'framer-motion';
import { useEffect, useState } from 'react';

interface Exploit {
  id: number;
  title: string;
  date: string;
  tags: string[];
  link: string;
  educational_insight: string;
}

interface Metadata {
  author: string;
  last_update: string;
  total_poc: number;
  exploits: Exploit[];
}

const getSeverity = (id: number): { level: string; class: string } => {
  if (id <= 3) return { level: 'Critical', class: 'severity-critical' };
  if (id <= 7) return { level: 'High', class: 'severity-high' };
  if (id <= 12) return { level: 'Medium', class: 'severity-medium' };
  return { level: 'Low', class: 'severity-low' };
};

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.2,
    },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 30 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.6, ease: [0.4, 0, 0.2, 1] },
  },
};

const staggerUp = {
  hidden: { opacity: 0, y: 40 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.7, ease: [0.4, 0, 0.2, 1] },
  },
};

export default function Home() {
  const [metadata, setMetadata] = useState<Metadata | null>(null);

  useEffect(() => {
    fetch('/metadata.json')
      .then((res) => res.json())
      .then(setMetadata)
      .catch(console.error);
  }, []);

  const stats = [
    { label: 'PoC Total', value: metadata?.total_poc || 18 },
    { label: 'Active Research', value: 4 },
    { label: 'Chain Support', value: 12 },
  ];

  return (
    <>
      <div className="mesh-gradient" aria-hidden="true" />
      
      <main>
        <section className="section" style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', paddingTop: '80px' }}>
          <div className="container">
            <motion.div
              variants={containerVariants}
              initial="hidden"
              animate="visible"
              style={{ textAlign: 'center', maxWidth: '800px', margin: '0 auto' }}
            >
              <motion.span
                variants={itemVariants}
                style={{
                  fontSize: '13px',
                  fontWeight: 500,
                  letterSpacing: '0.15em',
                  textTransform: 'uppercase',
                  color: 'var(--accent-purple)',
                  marginBottom: '24px',
                  display: 'block',
                }}
              >
                DeFi Security Vault
              </motion.span>
              
              <motion.h1
                variants={itemVariants}
                style={{
                  fontSize: 'clamp(48px, 10vw, 80px)',
                  fontWeight: 700,
                  letterSpacing: '-0.02em',
                  lineHeight: 1.1,
                  marginBottom: '20px',
                  background: 'linear-gradient(135deg, #FAFAFA 0%, #A1A1AA 100%)',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  backgroundClip: 'text',
                }}
              >
                Yudis-bit
              </motion.h1>
              
              <motion.p
                variants={itemVariants}
                style={{
                  fontSize: 'clamp(18px, 3vw, 24px)',
                  fontWeight: 300,
                  color: 'var(--text-secondary)',
                  letterSpacing: '0.01em',
                  maxWidth: '560px',
                  margin: '0 auto 40px',
                }}
              >
                The DeFi Security Vault
              </motion.p>
              
              <motion.p
                variants={itemVariants}
                style={{
                  fontSize: '16px',
                  color: 'var(--text-muted)',
                  maxWidth: '480px',
                  margin: '0 auto',
                  lineHeight: 1.7,
                }}
              >
                Uncovering vulnerabilities to build a more resilient Web3.
              </motion.p>
            </motion.div>
          </div>
        </section>

        <section className="section" style={{ paddingTop: 0 }}>
          <div className="container">
            <motion.div
              variants={containerVariants}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true, margin: '-100px' }}
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(3, 1fr)',
                gap: '20px',
              }}
            >
              {stats.map((stat, i) => (
                <motion.div
                  key={stat.label}
                  variants={itemVariants}
                  className="glass-card"
                  style={{
                    padding: '32px 24px',
                    textAlign: 'center',
                  }}
                >
                  <div
                    style={{
                      fontSize: 'clamp(36px, 6vw, 48px)',
                      fontWeight: 700,
                      letterSpacing: '-0.02em',
                      color: 'var(--text-primary)',
                      marginBottom: '8px',
                    }}
                  >
                    {stat.value}
                  </div>
                  <div
                    style={{
                      fontSize: '13px',
                      fontWeight: 500,
                      letterSpacing: '0.1em',
                      textTransform: 'uppercase',
                      color: 'var(--text-muted)',
                    }}
                  >
                    {stat.label}
                  </div>
                </motion.div>
              ))}
            </motion.div>
          </div>
        </section>

        <section className="section">
          <div className="container">
            <motion.div
              variants={staggerUp}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true, margin: '-50px' }}
            >
              <h2
                style={{
                  fontSize: 'clamp(28px, 5vw, 40px)',
                  fontWeight: 600,
                  letterSpacing: '-0.01em',
                  textAlign: 'center',
                  marginBottom: '60px',
                }}
              >
                Exploit Gallery
              </h2>
            </motion.div>
            
            <motion.div
              variants={containerVariants}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true, margin: '-50px' }}
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))',
                gap: '24px',
              }}
            >
              {metadata?.exploits.slice(0, 9).map((exploit) => {
                const severity = getSeverity(exploit.id);
                return (
                  <motion.a
                    key={exploit.id}
                    href={exploit.link}
                    target="_blank"
                    rel="noopener noreferrer"
                    variants={itemVariants}
                    className="glass-card"
                    style={{
                      padding: '28px',
                      display: 'flex',
                      flexDirection: 'column',
                      textDecoration: 'none',
                      color: 'inherit',
                    }}
                  >
                    <div
                      style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        marginBottom: '16px',
                      }}
                    >
                      <span
                        style={{
                          fontSize: '14px',
                          fontWeight: 500,
                          color: 'var(--text-secondary)',
                        }}
                      >
                        {exploit.date}
                      </span>
                      <span
                        className={severity.class}
                        style={{
                          fontSize: '11px',
                          fontWeight: 600,
                          letterSpacing: '0.05em',
                          textTransform: 'uppercase',
                          padding: '4px 10px',
                          borderRadius: '20px',
                        }}
                      >
                        {severity.level}
                      </span>
                    </div>
                    
                    <h3
                      style={{
                        fontSize: '20px',
                        fontWeight: 600,
                        marginBottom: '16px',
                      }}
                    >
                      {exploit.title}
                    </h3>
                    
                    <p
                      style={{
                        fontFamily: 'var(--font-serif)',
                        fontSize: '15px',
                        color: 'var(--text-secondary)',
                        fontStyle: 'italic',
                        lineHeight: 1.7,
                        flex: 1,
                      }}
                    >
                      "{exploit.educational_insight}"
                    </p>
                    
                    <div
                      style={{
                        display: 'flex',
                        gap: '8px',
                        marginTop: '20px',
                        flexWrap: 'wrap',
                      }}
                    >
                      {exploit.tags.map((tag) => (
                        <span
                          key={tag}
                          style={{
                            fontSize: '11px',
                            fontWeight: 500,
                            letterSpacing: '0.03em',
                            color: 'var(--text-muted)',
                            background: 'rgba(255,255,255,0.05)',
                            padding: '4px 10px',
                            borderRadius: '20px',
                          }}
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                  </motion.a>
                );
              })}
            </motion.div>
          </div>
        </section>

        <section className="section">
          <div className="container">
            <motion.div
              variants={staggerUp}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true, margin: '-50px' }}
            >
              <h2
                style={{
                  fontSize: 'clamp(28px, 5vw, 40px)',
                  fontWeight: 600,
                  letterSpacing: '-0.01em',
                  textAlign: 'center',
                  marginBottom: '16px',
                }}
              >
                Security Services
              </h2>
              <p
                style={{
                  fontSize: '16px',
                  color: 'var(--text-secondary)',
                  textAlign: 'center',
                  marginBottom: '60px',
                  maxWidth: '480px',
                  margin: '0 auto 60px',
                }}
              >
                Professional security solutions for your DeFi protocol.
              </p>
            </motion.div>
            
            <motion.div
              variants={containerVariants}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true, margin: '-50px' }}
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
                gap: '24px',
                maxWidth: '800px',
                margin: '0 auto',
              }}
            >
              <motion.div variants={itemVariants} className="glass-card" style={{ padding: '36px' }}>
                <div
                  style={{
                    width: '48px',
                    height: '48px',
                    borderRadius: '12px',
                    background: 'linear-gradient(135deg, var(--accent-indigo) 0%, var(--accent-violet) 100%)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    marginBottom: '24px',
                  }}
                >
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2">
                    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
                  </svg>
                </div>
                <h3 style={{ fontSize: '22px', fontWeight: 600, marginBottom: '12px' }}>
                  Protocol Audits
                </h3>
                <p style={{ fontSize: '15px', color: 'var(--text-secondary)', marginBottom: '24px', lineHeight: 1.7 }}>
                  Comprehensive security audits to identify vulnerabilities before deployment.
                </p>
                <button className="btn-primary" style={{ width: '100%' }}>
                  Hire Yudis-bit
                </button>
              </motion.div>
              
              <motion.div variants={itemVariants} className="glass-card" style={{ padding: '36px' }}>
                <div
                  style={{
                    width: '48px',
                    height: '48px',
                    borderRadius: '12px',
                    background: 'linear-gradient(135deg, var(--accent-violet) 0%, var(--accent-purple) 100%)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    marginBottom: '24px',
                  }}
                >
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2">
                    <polyline points="16 18 22 12 16 6" />
                    <polyline points="8 6 2 12 8 18" />
                  </svg>
                </div>
                <h3 style={{ fontSize: '22px', fontWeight: 600, marginBottom: '12px' }}>
                  PoC Development
                </h3>
                <p style={{ fontSize: '15px', color: 'var(--text-secondary)', marginBottom: '24px', lineHeight: 1.7 }}>
                  Proof-of-concept exploits to validate security assumptions.
                </p>
                <button className="btn-primary" style={{ width: '100%' }}>
                  Hire Yudis-bit
                </button>
              </motion.div>
            </motion.div>
          </div>
        </section>

        <footer
          style={{
            padding: '40px 24px',
            textAlign: 'center',
            borderTop: '1px solid var(--border-subtle)',
          }}
        >
          <div className="container">
            <p style={{ fontSize: '14px', color: 'var(--text-muted)' }}>
              © 2026 Yudis-bit. All rights reserved.
            </p>
          </div>
        </footer>
      </main>

      <button className="floating-cta">Audit Request</button>

      <style jsx global>{`
        @media (max-width: 768px) {
          .section .container {
            padding: 0 20px;
          }
        }
      `}</style>
    </>
  );
}