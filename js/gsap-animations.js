/* ==========================================================================
   CALIPR — GSAP Dreelio-Style Animations
   Handles page load sequence, scroll reveals, counters, parallax,
   particles, and micro-interactions.
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
  // Register GSAP plugins
  gsap.registerPlugin(ScrollTrigger);

  // Kill ScrollTrigger on page unload to prevent memory leaks
  window.addEventListener('beforeunload', () => ScrollTrigger.killAll());

  // ===== ANIMATION 1: PAGE LOAD SEQUENCE =====
  window.addEventListener('load', () => {
    const tl = gsap.timeline({ defaults: { ease: 'power3.out' } });

    // T=0.0s — Hackathon banner + Navbar
    tl.from('.hackathon-banner', { y: -40, opacity: 0, duration: 0.4, ease: 'power2.out' }, 0);
    tl.from('.navbar', { y: -64, opacity: 0, duration: 0.5, ease: 'power2.out' }, 0.1);

    // T=0.2s — Hero section label
    tl.from('.hero .section-label', { x: -24, opacity: 0, duration: 0.4 }, 0.2);

    // T=0.35s — H1 heading
    tl.from('.hero h1', { y: 48, opacity: 0, duration: 0.7 }, 0.35);

    // T=0.55s — Hero subtitle
    tl.from('.hero-subtitle', { y: 24, opacity: 0, duration: 0.5 }, 0.55);

    // T=0.7s — CTA buttons
    tl.from('.hero-ctas .btn', { scale: 0.9, opacity: 0, duration: 0.4, ease: 'back.out(1.4)', stagger: 0.1 }, 0.7);

    // T=1.0s — Dashboard mockup
    tl.from('.hero-mockup-wrapper', { y: 72, opacity: 0, scale: 0.95, duration: 0.9, ease: 'power2.out' }, 1.0);

    // Fade hero blobs in
    gsap.to('.hero-blob', { opacity: 1, duration: 1.2, stagger: 0.2, ease: 'power1.out', delay: 0.5 });
  });

  // ===== ANIMATION 2: DASHBOARD SCROLL REVEAL =====
  (function initDashboardReveal() {
    const wrapper = document.querySelector('.hero-mockup-wrapper');
    const frame = wrapper?.querySelector('.browser-frame');
    if (!wrapper || !frame) return;

    ScrollTrigger.create({
      trigger: wrapper,
      start: 'top 80%',
      end: 'top 20%',
      scrub: 0.8,
      onUpdate: (self) => {
        const p = self.progress;
        // Scale: 0.92 -> 1.0
        const scale = 0.92 + (0.08 * p);
        // Border radius: 16px -> 8px
        const radius = 16 - (8 * p);
        frame.style.transform = `scale(${scale})`;
        frame.style.borderRadius = `${radius}px`;
      }
    });
  })();

  // ===== ANIMATION 3: SCROLL-TRIGGERED SECTION REVEALS =====
  (function initScrollReveals() {
    // Section labels — slide from left
    gsap.utils.toArray('.section-label').forEach(el => {
      gsap.from(el, {
        scrollTrigger: { trigger: el, start: 'top 88%', once: true },
        x: -20, opacity: 0, duration: 0.5, ease: 'power2.out'
      });
    });

    // H2 section titles — fade up
    gsap.utils.toArray('.section-title').forEach(el => {
      gsap.from(el, {
        scrollTrigger: { trigger: el, start: 'top 85%', once: true },
        y: 40, opacity: 0, duration: 0.7, ease: 'power3.out'
      });
    });

    // Section subtitles — fade up
    gsap.utils.toArray('.section-subtitle').forEach(el => {
      gsap.from(el, {
        scrollTrigger: { trigger: el, start: 'top 88%', once: true },
        y: 20, opacity: 0, duration: 0.5, ease: 'power2.out', delay: 0.1
      });
    });

    // Bento cards — staggered
    const bentoCards = gsap.utils.toArray('.bento-card');
    if (bentoCards.length) {
      gsap.from(bentoCards, {
        scrollTrigger: { trigger: bentoCards[0], start: 'top 85%', once: true },
        y: 48, opacity: 0, duration: 0.6, ease: 'power2.out', stagger: 0.15
      });
    }

    // Signal cards — staggered
    const signalCards = gsap.utils.toArray('.signal-card');
    if (signalCards.length) {
      gsap.from(signalCards, {
        scrollTrigger: { trigger: signalCards[0], start: 'top 85%', once: true },
        y: 48, opacity: 0, duration: 0.6, ease: 'power2.out', stagger: 0.12
      });
    }

    // Benefit cards — staggered
    const benefitCards = gsap.utils.toArray('.benefit-card');
    if (benefitCards.length) {
      gsap.from(benefitCards, {
        scrollTrigger: { trigger: benefitCards[0], start: 'top 85%', once: true },
        y: 48, opacity: 0, duration: 0.6, ease: 'power2.out', stagger: 0.12
      });
    }

    // Pipeline steps — staggered slide up
    const pipelineSteps = gsap.utils.toArray('.pipeline-step');
    if (pipelineSteps.length) {
      gsap.from(pipelineSteps, {
        scrollTrigger: { trigger: pipelineSteps[0].parentElement, start: 'top 80%', once: true },
        y: 60, opacity: 0, duration: 0.6, ease: 'power2.out', stagger: 0.15
      });
    }

    // Pipeline connector fill animation
    const connectorFill = document.querySelector('.pipeline-connector-fill');
    if (connectorFill) {
      gsap.from(connectorFill, {
        scrollTrigger: { trigger: connectorFill.parentElement, start: 'top 80%', once: true },
        scaleX: 0, duration: 1.2, ease: 'power2.out', delay: 0.3
      });
    }

    // Pricing cards — staggered with scale
    const pricingCards = gsap.utils.toArray('.pricing-card');
    if (pricingCards.length) {
      gsap.from(pricingCards, {
        scrollTrigger: { trigger: pricingCards[0], start: 'top 85%', once: true },
        y: 48, opacity: 0, scale: 0.95, duration: 0.6, ease: 'back.out(1.2)', stagger: 0.12
      });
    }

    // Metric cards — scale in
    const metricCards = gsap.utils.toArray('.metric-card');
    if (metricCards.length) {
      gsap.from(metricCards, {
        scrollTrigger: { trigger: metricCards[0], start: 'top 88%', once: true },
        scale: 0.92, opacity: 0, duration: 0.5, ease: 'back.out(1.3)', stagger: 0.1
      });
    }

    // Demo section — candidate card + radar
    const demoContent = document.querySelector('.demo-content');
    if (demoContent) {
      gsap.from('.demo-tabs', {
        scrollTrigger: { trigger: demoContent, start: 'top 85%', once: true },
        y: 20, opacity: 0, duration: 0.5, ease: 'power2.out'
      });
      gsap.from('.candidate-card', {
        scrollTrigger: { trigger: demoContent, start: 'top 80%', once: true },
        x: -40, opacity: 0, duration: 0.7, ease: 'power2.out', delay: 0.15
      });
      gsap.from('.radar-wrapper', {
        scrollTrigger: { trigger: demoContent, start: 'top 80%', once: true },
        x: 40, opacity: 0, duration: 0.7, ease: 'power2.out', delay: 0.15
      });
    }

    // Contact section
    const contactInfo = document.querySelector('.contact-info');
    const contactCard = document.querySelector('.contact-card');
    if (contactInfo) {
      gsap.from(contactInfo, {
        scrollTrigger: { trigger: contactInfo, start: 'top 80%', once: true },
        x: -40, opacity: 0, duration: 0.7, ease: 'power2.out'
      });
    }
    if (contactCard) {
      gsap.from(contactCard, {
        scrollTrigger: { trigger: contactCard, start: 'top 80%', once: true },
        x: 40, opacity: 0, duration: 0.7, ease: 'power2.out', delay: 0.15
      });
    }

    // CTA section
    const ctaSection = document.querySelector('.cta-section');
    if (ctaSection) {
      gsap.from(ctaSection.querySelectorAll('h2, .section-subtitle, .cta-buttons'), {
        scrollTrigger: { trigger: ctaSection, start: 'top 80%', once: true },
        y: 40, opacity: 0, duration: 0.7, ease: 'power3.out', stagger: 0.15
      });
    }

    // Problem/Solution grid
    const psColumns = gsap.utils.toArray('.ps-column');
    if (psColumns.length) {
      gsap.from(psColumns, {
        scrollTrigger: { trigger: psColumns[0], start: 'top 85%', once: true },
        y: 40, opacity: 0, duration: 0.7, ease: 'power2.out', stagger: 0.2
      });
    }

    // Footer
    const footerGrid = document.querySelector('.footer-grid');
    if (footerGrid) {
      gsap.from(footerGrid.children, {
        scrollTrigger: { trigger: footerGrid, start: 'top 90%', once: true },
        y: 30, opacity: 0, duration: 0.5, ease: 'power2.out', stagger: 0.1
      });
    }
  })();

  // ===== ANIMATION 4: METRIC COUNTERS (GSAP-powered) =====
  (function initGSAPCounters() {
    document.querySelectorAll('.metric-value').forEach(counter => {
      const target = parseFloat(counter.dataset.target);
      const isDecimal = counter.dataset.decimal === 'true';
      const prefix = counter.dataset.prefix || '';
      const suffix = counter.dataset.suffix || '';

      // Set initial text
      counter.textContent = prefix + '0' + suffix;

      ScrollTrigger.create({
        trigger: counter,
        start: 'top 85%',
        once: true,
        onEnter: () => {
          const obj = { val: 0 };
          gsap.to(obj, {
            val: target,
            duration: 1.6,
            ease: 'power2.out',
            onUpdate: () => {
              if (isDecimal) {
                counter.textContent = prefix + obj.val.toFixed(2) + suffix;
              } else {
                counter.textContent = prefix + Math.floor(obj.val) + suffix;
              }
            },
            onComplete: () => {
              counter.textContent = isDecimal
                ? prefix + target.toFixed(2) + suffix
                : prefix + target + suffix;
            }
          });
        }
      });
    });
  })();

  // ===== ANIMATION 5: PARTICLES =====
  (function initParticles() {
    const hero = document.querySelector('.hero');
    if (!hero) return;

    for (let i = 0; i < 20; i++) {
      const particle = document.createElement('div');
      particle.className = 'particle';
      particle.style.cssText = `
        left: ${Math.random() * 100}%;
        bottom: ${Math.random() * 40}%;
        animation-duration: ${6 + Math.random() * 8}s;
        animation-delay: ${Math.random() * 8}s;
        --drift: ${(Math.random() - 0.5) * 60}px;
        width: ${1 + Math.random() * 3}px;
        height: ${1 + Math.random() * 3}px;
      `;
      hero.appendChild(particle);
    }
  })();

  // ===== ANIMATION 6: NAVBAR HIDE/SHOW ON SCROLL =====
  (function initNavbarHideShow() {
    const navbar = document.getElementById('navbar');
    if (!navbar) return;

    let lastScroll = 0;

    window.addEventListener('scroll', () => {
      const scrolled = window.scrollY;

      // Hide navbar on scroll down, show on scroll up
      if (scrolled > lastScroll && scrolled > 200) {
        navbar.style.transform = 'translateX(-50%) translateY(-150%)';
      } else {
        navbar.style.transform = 'translateX(-50%) translateY(0)';
      }

      lastScroll = scrolled;
    }, { passive: true });
  })();

  // ===== ANIMATION 7: MARQUEE PAUSE ON HOVER =====
  (function initMarqueeHover() {
    const track = document.getElementById('marqueeTrack');
    if (!track) return;
    
    track.addEventListener('mouseenter', () => {
      track.style.animationPlayState = 'paused';
    });
    track.addEventListener('mouseleave', () => {
      track.style.animationPlayState = 'running';
    });
  })();

  // ===== ANIMATION 8: HERO CLOUD PARALLAX =====
  function initHeroCloudParallax() {
    const hero = document.querySelector('.hero');
    if (!hero) return;

    // Layer 1 — slowest (0.15x scroll speed) — furthest back
    gsap.to('.cloud-layer-1', {
      y: () => hero.offsetHeight * 0.15,
      ease: 'none',
      scrollTrigger: {
        trigger: hero,
        start: 'top top',
        end: 'bottom top',
        scrub: 1.2,
      }
    });

    // Layer 2 — medium (0.30x scroll speed)
    gsap.to('.cloud-layer-2', {
      y: () => hero.offsetHeight * 0.30,
      ease: 'none',
      scrollTrigger: {
        trigger: hero,
        start: 'top top',
        end: 'bottom top',
        scrub: 0.9,
      }
    });

    // Layer 3 — fastest (0.50x scroll speed) — closest
    gsap.to('.cloud-layer-3', {
      y: () => hero.offsetHeight * 0.50,
      ease: 'none',
      scrollTrigger: {
        trigger: hero,
        start: 'top top',
        end: 'bottom top',
        scrub: 0.6,
      }
    });

    // Fade ALL clouds out as hero exits viewport
    gsap.to('.cloud-scene', {
      opacity: 0,
      ease: 'none',
      scrollTrigger: {
        trigger: hero,
        start: '60% top',
        end: 'bottom top',
        scrub: true,
      }
    });

    // Fade clouds IN on page load
    window.addEventListener('load', () => {
      gsap.from('.cloud-scene', {
        opacity: 0,
        duration: 1.8,
        ease: 'power1.out',
        delay: 0.5,
      });
    });
  }

  // ===== ANIMATION 9: CTA CLOUD PARALLAX & REVEAL =====
  function initCTACloudEffect() {
    const ctaSection = document.querySelector('.cta-section');
    if (!ctaSection) return;

    const backLayer  = ctaSection.querySelector('.cta-cloud-back');
    const frontLayer = ctaSection.querySelector('.cta-cloud-front');
    const sky        = ctaSection.querySelector('.cta-sky');

    if (!backLayer || !frontLayer) return;

    // REVEAL — clouds rise from below as CTA enters viewport
    gsap.from(backLayer, {
      y: 80,
      opacity: 0,
      duration: 1.4,
      ease: 'power2.out',
      scrollTrigger: {
        trigger: ctaSection,
        start: 'top 85%',
        once: true,
      }
    });

    gsap.from(frontLayer, {
      y: 40,
      opacity: 0,
      duration: 1.0,
      ease: 'power2.out',
      delay: 0.3,
      scrollTrigger: {
        trigger: ctaSection,
        start: 'top 85%',
        once: true,
      }
    });

    // PARALLAX — back layer moves UP slowly as you scroll through CTA
    gsap.to(backLayer, {
      y: -80,
      ease: 'none',
      scrollTrigger: {
        trigger: ctaSection,
        start: 'top bottom',
        end: 'bottom top',
        scrub: 1.5,
      }
    });

    // PARALLAX — front layer moves UP faster (stronger parallax = closer feeling)
    gsap.to(frontLayer, {
      y: -140,
      ease: 'none',
      scrollTrigger: {
        trigger: ctaSection,
        start: 'top bottom',
        end: 'bottom top',
        scrub: 0.8,
      }
    });

    // SKY gradient shifts slightly warmer as you scroll deeper
    gsap.to(sky, {
      opacity: 0.85,
      ease: 'none',
      scrollTrigger: {
        trigger: ctaSection,
        start: 'top center',
        end: 'bottom top',
        scrub: true,
      }
    });
  }

  // Initialize Cloud Animations
  initHeroCloudParallax();
  initCTACloudEffect();

  // Respects user accessibility settings
  const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (prefersReduced) {
    document.querySelectorAll('.cloud-a, .cloud-b, .cloud-c, .cloud-d, .cloud-e, .cloud-f, .cloud-g, .cb-1, .cb-2, .cb-3, .cb-4, .cf-1, .cf-2, .cf-3')
      .forEach(el => {
        el.style.animation = 'none';
      });
  }

  // Refresh after fonts and images load
  window.addEventListener('load', () => {
    ScrollTrigger.refresh();
  });

  // Refresh ScrollTrigger after fonts load
  document.fonts.ready.then(() => ScrollTrigger.refresh());
});
