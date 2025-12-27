// Auto-detect Hebrew text and apply RTL direction
(function () {
  const HEBREW_REGEX = /[\u0590-\u05FF]/;

  function hasHebrew(text) {
    return HEBREW_REGEX.test(text);
  }

  function applyRTL(element) {
    if (hasHebrew(element.textContent)) {
      element.style.direction = "rtl";
      element.style.textAlign = "right";
    }
  }

  // Handle chat input RTL as user types (using event delegation)
  function setupInputRTL() {
    document.addEventListener("input", (e) => {
      const target = e.target;
      if (target.id === "chat-input") {
        if (hasHebrew(target.value)) {
          target.style.direction = "rtl";
          target.style.textAlign = "right";
        } else {
          target.style.direction = "ltr";
          target.style.textAlign = "left";
        }
      }
    });
  }

  // Apply RTL to messages (not steps)
  function processMessages() {
    // Target the actual text containers inside prose
    const articles = document.querySelectorAll('.prose div[role="article"]');
    articles.forEach((article) => {
      // Skip if already processed
      if (article.dataset.rtlProcessed) return;

      // Check parent step type - only process user_message and assistant_message
      const stepContainer = article.closest("[data-step-type]");
      const stepType = stepContainer?.getAttribute("data-step-type");

      // Skip tool/llm steps, only process actual messages
      if (stepType && stepType !== "user_message" && stepType !== "assistant_message") {
        return;
      }

      applyRTL(article);
      article.dataset.rtlProcessed = "true";
    });

    // Also handle list items inside prose (for assistant messages with bullets)
    const listItems = document.querySelectorAll('.prose li');
    listItems.forEach((li) => {
      if (li.dataset.rtlProcessed) return;

      const stepContainer = li.closest("[data-step-type]");
      const stepType = stepContainer?.getAttribute("data-step-type");

      if (stepType && stepType !== "user_message" && stepType !== "assistant_message") {
        return;
      }

      applyRTL(li);
      li.dataset.rtlProcessed = "true";
    });
  }

  // Observe DOM changes for new messages
  function observeMessages() {
    const observer = new MutationObserver((mutations) => {
      let shouldProcess = false;
      for (const mutation of mutations) {
        if (mutation.addedNodes.length > 0) {
          shouldProcess = true;
          break;
        }
      }
      if (shouldProcess) {
        processMessages();
      }
    });

    observer.observe(document.body, {
      childList: true,
      subtree: true,
    });
  }

  // Initialize when DOM is ready
  function init() {
    processMessages();
    setupInputRTL();
    observeMessages();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
