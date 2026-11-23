// For base.html
//  Shared javascript functions and actions

(function () {
  // Highlight the current page in the navbar
  var path = window.location.pathname.replace(/\/+$/, "") || "/";
  document.querySelectorAll(".navbar-nav .nav-link").forEach(function (link) {
    var href = (link.getAttribute("href") || "").replace(/\/+$/, "") || "/";
    if (href === path) {
      link.classList.add("active");
      link.setAttribute("aria-current", "page");
    }
  });

  // Add a stronger shadow to the navbar once the page is scrolled
  var nav = document.querySelector(".navbar");
  if (nav) {
    var onScroll = function () {
      nav.classList.toggle("scrolled", window.scrollY > 8);
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
  }

  // Copy buttons (used on the contact page)
  document.querySelectorAll("[data-copy]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var text = btn.getAttribute("data-copy");
      var done = function () {
        var old = btn.textContent;
        btn.textContent = "Copied!";
        btn.classList.add("copied");
        setTimeout(function () {
          btn.textContent = old;
          btn.classList.remove("copied");
        }, 1600);
      };
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(done).catch(function () {});
      } else {
        var ta = document.createElement("textarea");
        ta.value = text;
        document.body.appendChild(ta);
        ta.select();
        try { document.execCommand("copy"); done(); } catch (e) {}
        document.body.removeChild(ta);
      }
    });
  });
})();
