(function () {
  const toggle = document.getElementById("nav-toggle");
  const nav = document.getElementById("navbar-nav");
  const year = document.getElementById("year");

  if (year) {
    year.textContent = String(new Date().getFullYear());
  }

  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      const open = nav.classList.toggle("open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
      toggle.innerHTML = open
        ? '<i class="fas fa-times"></i>'
        : '<i class="fas fa-bars"></i>';
    });

    nav.querySelectorAll("a").forEach(function (link) {
      link.addEventListener("click", function () {
        const href = link.getAttribute("href") || "";
        const targetFile = href.split("#")[0];
        const samePage =
          !targetFile ||
          targetFile === pageFile ||
          (isHome && (targetFile === "index.html" || targetFile === ""));
        if (!samePage) return;
        nav.classList.remove("open");
        toggle.setAttribute("aria-expanded", "false");
        toggle.innerHTML = '<i class="fas fa-bars"></i>';
      });
    });
  }

  const sections = document.querySelectorAll("section[id]");
  const navLinks = document.querySelectorAll(".navbar-nav a");
  const pageFile = (window.location.pathname.split("/").pop() || "index.html");
  const isHome = pageFile === "" || pageFile === "index.html";

  function setActiveLink() {
    if (!isHome) {
      navLinks.forEach(function (link) {
        const href = (link.getAttribute("href") || "").split("#")[0];
        link.classList.toggle("active", href === pageFile);
      });
      return;
    }

    const scrollY = window.scrollY + 90;
    let current = "about";
    sections.forEach(function (section) {
      if (scrollY >= section.offsetTop) {
        current = section.getAttribute("id");
      }
    });
    const homeMap = {
      about: "index.html",
      publications: "publications.html",
    };
    const activeHref = homeMap[current] || "index.html";
    navLinks.forEach(function (link) {
      link.classList.toggle("active", link.getAttribute("href") === activeHref);
    });
  }

  if (isHome) {
    window.addEventListener("scroll", setActiveLink, { passive: true });
  }
  setActiveLink();

  // Topic filters (articles + publications)
  const cards = document.querySelectorAll(".article-card");

  document.querySelectorAll(".article-filters").forEach(function (filters) {
    const scope = filters.parentElement;
    const topics = scope.querySelectorAll(".article-topic");

    function applyFilter(filter) {
      topics.forEach(function (topic) {
        const show = filter === "all" || topic.getAttribute("data-cat") === filter;
        topic.classList.toggle("hidden", !show);
      });
    }

    filters.addEventListener("click", function (e) {
      const btn = e.target.closest(".filter-btn");
      if (!btn) return;

      filters.querySelectorAll(".filter-btn").forEach(function (b) {
        b.classList.remove("active");
      });
      btn.classList.add("active");

      applyFilter(btn.getAttribute("data-filter"));
    });

    const select = filters.querySelector(".filter-select");
    if (select) {
      select.addEventListener("change", function () {
        applyFilter(select.value);
      });
    }
  });

  // Citation counts are loaded from the cache refreshed by the scheduled updater.
  const scholarItems = document.querySelectorAll("[data-scholar-title]");
  const scholarTotals = document.querySelectorAll("[data-scholar-total]");

  function normalizeScholarTitle(title) {
    return title
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, " ")
      .split(" ")
      .filter(function (word) {
        return word && !["a", "an", "the"].includes(word);
      })
      .join(" ");
  }

  if (scholarItems.length || scholarTotals.length) {
    fetch("data/scholar-citations.json", { cache: "no-store" })
      .then(function (response) {
        if (!response.ok) throw new Error("Citation data is unavailable");
        return response.json();
      })
      .then(function (data) {
        const citationMap = new Map();
        data.publications.forEach(function (publication) {
          citationMap.set(normalizeScholarTitle(publication.title), publication);
        });

        scholarTotals.forEach(function (total) {
          total.textContent = data.total_citations.toLocaleString();
          total.closest("a").title =
            "Google Scholar citations · Updated " +
            new Date(data.updated_at).toLocaleDateString();
        });

        scholarItems.forEach(function (item) {
          const publication = citationMap.get(
            normalizeScholarTitle(item.getAttribute("data-scholar-title"))
          );
          if (!publication) return;

          const citationLink = item.querySelector("[data-scholar-citations]");
          if (!citationLink) return;
          citationLink.textContent =
            "Cited by " + publication.citations.toLocaleString();
          citationLink.href = publication.url || data.profile_url;
        });
      })
      .catch(function () {
        scholarTotals.forEach(function (total) {
          total.textContent = "unavailable";
        });
      });
  }

  cards.forEach(function (card) {
    const link = card.querySelector("h3 a");
    if (!link) return;
    card.addEventListener("click", function (e) {
      if (e.target.closest("a")) return;
      window.open(link.href, link.target || "_blank", "noopener");
    });
  });

  // CV preview modal
  const cvModal = document.getElementById("cv-modal");
  const cvPreviewBtn = document.getElementById("cv-preview-btn");

  function openCvModal() {
    if (!cvModal) return;
    cvModal.hidden = false;
    document.body.classList.add("cv-modal-open");
  }

  function closeCvModal() {
    if (!cvModal) return;
    cvModal.hidden = true;
    document.body.classList.remove("cv-modal-open");
  }

  if (cvPreviewBtn) {
    cvPreviewBtn.addEventListener("click", openCvModal);
  }

  if (cvModal) {
    cvModal.querySelectorAll("[data-cv-close]").forEach(function (el) {
      el.addEventListener("click", closeCvModal);
    });
  }

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && cvModal && !cvModal.hidden) {
      closeCvModal();
    }
  });
})();
