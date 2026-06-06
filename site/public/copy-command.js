(function () {
  function copyText(text) {
    if (navigator.clipboard && window.isSecureContext) {
      return navigator.clipboard.writeText(text);
    }

    var area = document.createElement("textarea");
    area.value = text;
    area.setAttribute("readonly", "");
    area.style.position = "fixed";
    area.style.left = "-9999px";
    area.style.top = "-9999px";
    document.body.appendChild(area);
    area.select();

    try {
      document.execCommand("copy");
    } finally {
      document.body.removeChild(area);
    }

    return Promise.resolve();
  }

  function cleanCommand(text) {
    return text
      .replace(/^\s*\$\s?/gm, "")
      .replace(/^\s*>\s?/gm, "")
      .trim();
  }

  function enhancePre(pre, index) {
    if (!pre || pre.dataset.copyEnhanced === "true") return;

    var raw = pre.innerText || pre.textContent || "";
    var text = cleanCommand(raw);

    if (!text) return;

    pre.dataset.copyEnhanced = "true";

    var shell = document.createElement("div");
    shell.className = "ax-copy-shell";

    var parent = pre.parentNode;
    parent.insertBefore(shell, pre);
    shell.appendChild(pre);

    var button = document.createElement("button");
    button.type = "button";
    button.className = "ax-copy-button";
    button.setAttribute("aria-label", "Copy command block " + (index + 1));
    button.setAttribute("title", "Copy command");
    button.innerHTML = '<span aria-hidden="true">⧉</span><span class="sr-only">Copy</span>';

    button.addEventListener("click", function () {
      copyText(text)
        .then(function () {
          button.classList.add("is-copied");
          button.setAttribute("title", "Copied");
          button.innerHTML = '<span aria-hidden="true">✓</span><span class="sr-only">Copied</span>';

          window.setTimeout(function () {
            button.classList.remove("is-copied");
            button.setAttribute("title", "Copy command");
            button.innerHTML = '<span aria-hidden="true">⧉</span><span class="sr-only">Copy</span>';
          }, 1300);
        })
        .catch(function () {
          button.classList.add("is-failed");
          button.setAttribute("title", "Copy failed");
          button.innerHTML = '<span aria-hidden="true">!</span><span class="sr-only">Copy failed</span>';

          window.setTimeout(function () {
            button.classList.remove("is-failed");
            button.setAttribute("title", "Copy command");
            button.innerHTML = '<span aria-hidden="true">⧉</span><span class="sr-only">Copy</span>';
          }, 1300);
        });
    });

    shell.appendChild(button);
  }

  function initCopyButtons() {
    document.querySelectorAll("pre").forEach(enhancePre);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initCopyButtons);
  } else {
    initCopyButtons();
  }
})();
