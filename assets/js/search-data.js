// get the ninja-keys element
const ninja = document.querySelector('ninja-keys');

// add the home and posts menu items
ninja.data = [{
    id: "nav-about",
    title: "about",
    section: "Navigation",
    handler: () => {
      window.location.href = "/";
    },
  },{id: "nav-publications",
          title: "publications",
          description: "Peer-reviewed articles and book chapters, newest first.",
          section: "Navigation",
          handler: () => {
            window.location.href = "/publications/";
          },
        },{id: "nav-projects",
          title: "projects",
          description: "Current research programs.",
          section: "Navigation",
          handler: () => {
            window.location.href = "/projects/";
          },
        },{id: "news-new-paper-in-science-advances-rapid-high-sensitivity-screening-of-pregnancy-complications-by-profiling-circulating-placental-evs",
          title: 'New paper in Science Advances: rapid, high-sensitivity screening of pregnancy complications by profiling...',
          description: "",
          section: "News",},{id: "news-new-paper-in-small-a-plasmonic-mesoporous-gold-sers-biosensor-for-ovarian-cancer-derived-evs",
          title: 'New paper in Small: a plasmonic mesoporous gold SERS biosensor for ovarian cancer-derived...',
          description: "",
          section: "News",},{id: "news-new-paper-in-advanced-science-scalable-engineering-of-bio-manufactured-evs-for-selective-delivery-in-ovarian-cancer-patient-derived-models",
          title: 'New paper in Advanced Science: scalable engineering of bio-manufactured EVs for selective delivery...',
          description: "",
          section: "News",},{id: "news-new-paper-in-journal-of-extracellular-vesicles-small-ev-and-total-lipid-profiles-give-a-diagnostic-advantage-over-ca-125-across-ovarian-cancer-subtypes",
          title: 'New paper in Journal of Extracellular Vesicles: small EV and total lipid profiles...',
          description: "",
          section: "News",},{id: "projects-ovarian-cancer-early-detection",
          title: 'Ovarian cancer early detection',
          description: "Blood-based extracellular vesicle biomarkers for detecting ovarian cancer earlier",
          section: "Projects",handler: () => {
              window.location.href = "/projects/1_ovarian_cancer_detection/";
            },},{id: "projects-pregnancy-complications",
          title: 'Pregnancy complications',
          description: "Placental extracellular vesicles in gestational diabetes, preeclampsia and preterm birth",
          section: "Projects",handler: () => {
              window.location.href = "/projects/2_pregnancy_complications/";
            },},{id: "projects-ev-isolation-and-proteomics-methods",
          title: 'EV isolation and proteomics methods',
          description: "Reproducible extracellular vesicle isolation and DIA mass spectrometry workflows",
          section: "Projects",handler: () => {
              window.location.href = "/projects/3_ev_proteomics_methods/";
            },},{
        id: 'social-email',
        title: 'email',
        section: 'Socials',
        handler: () => {
          window.open("mailto:%61.%6C%61%69@%75%71.%65%64%75.%61%75", "_blank");
        },
      },{
        id: 'social-orcid',
        title: 'ORCID',
        section: 'Socials',
        handler: () => {
          window.open("https://orcid.org/0000-0002-4424-8767", "_blank");
        },
      },{
        id: 'social-linkedin',
        title: 'LinkedIn',
        section: 'Socials',
        handler: () => {
          window.open("https://www.linkedin.com/in/1andrewlai", "_blank");
        },
      },{
        id: 'social-scholar',
        title: 'Google Scholar',
        section: 'Socials',
        handler: () => {
          window.open("https://scholar.google.com/citations?user=5k2FlJcAAAAJ", "_blank");
        },
      },{
        id: 'social-scopus',
        title: 'Scopus',
        section: 'Socials',
        handler: () => {
          window.open("https://www.scopus.com/authid/detail.uri?authorId=57192718468", "_blank");
        },
      },{
      id: 'light-theme',
      title: 'Change theme to light',
      description: 'Change the theme of the site to Light',
      section: 'Theme',
      handler: () => {
        setThemeSetting("light");
      },
    },
    {
      id: 'dark-theme',
      title: 'Change theme to dark',
      description: 'Change the theme of the site to Dark',
      section: 'Theme',
      handler: () => {
        setThemeSetting("dark");
      },
    },
    {
      id: 'system-theme',
      title: 'Use system default theme',
      description: 'Change the theme of the site to System Default',
      section: 'Theme',
      handler: () => {
        setThemeSetting("system");
      },
    },];
