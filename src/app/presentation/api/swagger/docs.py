from fastapi import FastAPI
from fastapi.openapi.docs import (
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from fastapi.responses import HTMLResponse

SWAGGER_UI_THEME = """
<style>
  :root {
    color-scheme: light;
    --swagger-bg: #f6f8fb;
    --swagger-surface: #ffffff;
    --swagger-surface-muted: #f1f5f9;
    --swagger-text: #18212f;
    --swagger-text-muted: #64748b;
    --swagger-border: #d9e1ea;
    --swagger-shadow: 0 8px 28px rgba(15, 23, 42, 0.08);
  }

  html[data-swagger-theme="dark"] {
    color-scheme: dark;
    --swagger-bg: #0b1120;
    --swagger-surface: #111827;
    --swagger-surface-muted: #1e293b;
    --swagger-text: #e5edf7;
    --swagger-text-muted: #94a3b8;
    --swagger-border: #334155;
    --swagger-shadow: 0 10px 32px rgba(0, 0, 0, 0.28);
  }

  body,
  .swagger-ui {
    background: var(--swagger-bg);
    color: var(--swagger-text);
    transition: background-color 180ms ease, color 180ms ease;
  }

  .swagger-ui .info .title,
  .swagger-ui .info li,
  .swagger-ui .info p,
  .swagger-ui .info table,
  .swagger-ui .opblock-tag,
  .swagger-ui .opblock .opblock-summary-description,
  .swagger-ui .opblock-description-wrapper,
  .swagger-ui .opblock-description-wrapper p,
  .swagger-ui .parameter__name,
  .swagger-ui .parameter__type,
  .swagger-ui .response-col_status,
  .swagger-ui .response-col_description,
  .swagger-ui .responses-inner h4,
  .swagger-ui .responses-inner h5,
  .swagger-ui .model-title,
  .swagger-ui .model,
  .swagger-ui .model-box,
  .swagger-ui section.models h4,
  .swagger-ui label,
  .swagger-ui table thead tr td,
  .swagger-ui table thead tr th,
  .swagger-ui .tab li,
  .swagger-ui .scheme-container .schemes > label {
    color: var(--swagger-text);
  }

  .swagger-ui .info .base-url,
  .swagger-ui .opblock-tag small,
  .swagger-ui .parameter__deprecated,
  .swagger-ui .parameter__in {
    color: var(--swagger-text-muted);
  }

  .swagger-ui .scheme-container,
  .swagger-ui section.models,
  .swagger-ui .model-container,
  .swagger-ui .opblock .opblock-section-header,
  .swagger-ui .dialog-ux .modal-ux,
  .swagger-ui select,
  .swagger-ui input[type="text"],
  .swagger-ui input[type="password"],
  .swagger-ui input[type="email"],
  .swagger-ui textarea {
    background: var(--swagger-surface);
    color: var(--swagger-text);
    border-color: var(--swagger-border);
  }

  /* Swagger's invalid-field background is light even when dark mode is active. */
  html[data-swagger-theme="dark"] .swagger-ui input.invalid,
  html[data-swagger-theme="dark"] .swagger-ui textarea.invalid,
  html[data-swagger-theme="dark"] .swagger-ui select.invalid {
    background: #2b1b25 !important;
    color: var(--swagger-text);
    border-color: #f87171;
  }

  html[data-swagger-theme="dark"] .swagger-ui input.invalid::placeholder,
  html[data-swagger-theme="dark"] .swagger-ui textarea.invalid::placeholder {
    color: var(--swagger-text-muted);
    opacity: 1;
  }

  .swagger-ui .scheme-container,
  .swagger-ui section.models,
  .swagger-ui .dialog-ux .modal-ux {
    box-shadow: var(--swagger-shadow);
  }

  .swagger-ui section.models,
  .swagger-ui section.models .model-container,
  .swagger-ui .opblock-tag,
  .swagger-ui .opblock .opblock-section-header,
  .swagger-ui .dialog-ux .modal-ux-header {
    border-color: var(--swagger-border);
  }

  .swagger-ui .json-schema-2020-12 button {
    appearance: none;
    padding-block: 0;
    border: 0;
    outline: 0;
    background: transparent !important;
    box-shadow: none;
  }

  .swagger-ui .json-schema-2020-12 button:hover,
  .swagger-ui .json-schema-2020-12 button:focus,
  .swagger-ui .json-schema-2020-12 button:active {
    background: transparent !important;
    box-shadow: none;
  }

  html[data-swagger-theme="dark"] .swagger-ui .opblock {
    box-shadow: none;
  }

  html[data-swagger-theme="dark"] .swagger-ui .opblock .opblock-summary-path,
  html[data-swagger-theme="dark"] .swagger-ui .opblock .opblock-summary-path__deprecated,
  html[data-swagger-theme="dark"] .swagger-ui .opblock .opblock-summary-description {
    color: #dbd3d3;
  }

  html[data-swagger-theme="dark"] .swagger-ui .model-title,
  html[data-swagger-theme="dark"] .swagger-ui .model-box-control,
  html[data-swagger-theme="dark"] .swagger-ui .model-box-control span,
  html[data-swagger-theme="dark"] .swagger-ui .model .property,
  html[data-swagger-theme="dark"] .swagger-ui .model .property.primitive,
  html[data-swagger-theme="dark"] .swagger-ui .prop-name,
  html[data-swagger-theme="dark"] .swagger-ui .prop-type,
  html[data-swagger-theme="dark"] .swagger-ui .prop-format,
  html[data-swagger-theme="dark"] .swagger-ui .model .property-type,
  html[data-swagger-theme="dark"] .swagger-ui .model-toggle::after {
    color: #dbd3d3;
  }

  html[data-swagger-theme="dark"] .swagger-ui .model-box-control {
    padding: 0;
    border: 0;
    outline: 0;
    background: transparent !important;
    box-shadow: none;
  }

  html[data-swagger-theme="dark"] .swagger-ui .model-box-control:hover,
  html[data-swagger-theme="dark"] .swagger-ui .model-box-control:focus,
  html[data-swagger-theme="dark"] .swagger-ui .model-box-control:active {
    background: transparent !important;
    box-shadow: none;
  }

  html[data-swagger-theme="dark"] .swagger-ui .model-box,
  html[data-swagger-theme="dark"] .swagger-ui .model-container {
    background: #0f172a;
  }

  html[data-swagger-theme="dark"] .swagger-ui .model .description {
    color: #dbd3d3;
  }

  html[data-swagger-theme="dark"] .swagger-ui .json-schema-2020-12,
  html[data-swagger-theme="dark"] .swagger-ui .json-schema-2020-12 * {
    color: #dbd3d3 !important;
  }

  html[data-swagger-theme="dark"] .swagger-ui .json-schema-2020-12 svg {
    fill: #dbd3d3;
  }

  html[data-swagger-theme="dark"] .swagger-ui .highlight-code,
  html[data-swagger-theme="dark"] .swagger-ui .microlight {
    background: #070b14 !important;
    color: #dbeafe !important;
  }

  html[data-swagger-theme="dark"] .swagger-ui svg {
    fill: currentColor;
  }

  #swagger-theme-toggle {
    position: fixed;
    z-index: 10000;
    top: 14px;
    right: 18px;
    display: inline-flex;
    align-items: center;
    gap: 9px;
    min-width: 108px;
    height: 38px;
    padding: 0 13px;
    border: 1px solid var(--swagger-border);
    border-radius: 999px;
    background: color-mix(in srgb, var(--swagger-surface) 88%, transparent);
    color: var(--swagger-text);
    box-shadow: var(--swagger-shadow);
    backdrop-filter: blur(12px);
    cursor: pointer;
    font: 600 13px/1 system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    transition: transform 160ms ease, background-color 180ms ease, border-color 180ms ease;
  }

  #swagger-theme-toggle:hover {
    transform: translateY(-1px);
    background: var(--swagger-surface-muted);
  }

  #swagger-theme-toggle:focus-visible {
    outline: 3px solid rgba(59, 130, 246, 0.35);
    outline-offset: 2px;
  }

  #swagger-theme-toggle .theme-icon {
    font-size: 16px;
    line-height: 1;
  }

  @media (max-width: 640px) {
    #swagger-theme-toggle {
      min-width: 38px;
      width: 38px;
      padding: 0;
      justify-content: center;
    }

    #swagger-theme-toggle .theme-label {
      display: none;
    }
  }
</style>
"""

SWAGGER_UI_CUSTOM_SCRIPT = """
<script>
  (function () {
    const TARGETS = new Set([
      "client credentials location:",
      "client_id:",
      "client_secret:",
    ]);

    function normalize(text) {
      return (text || "").trim().toLowerCase().replace(/\\s+/g, " ");
    }

    function isTargetNode(node) {
      return TARGETS.has(normalize(node.textContent));
    }

    function hideControlNode(node) {
      if (!node) {
        return;
      }
      node.style.display = "none";
    }

    function hideFieldContainer(labelNode) {
      const directContainer = labelNode.parentElement;
      if (
        directContainer &&
        !directContainer.querySelector("input, select, button") &&
        normalize(directContainer.textContent).length < 100
      ) {
        directContainer.style.display = "none";
        return;
      }

      let container = labelNode.parentElement;
      while (container && container !== document.body) {
        const hasControl = !!container.querySelector("input, select");
        const hasActionButton = !!container.querySelector("button, .btn");
        if (hasControl && !hasActionButton) {
          container.style.display = "none";
          return;
        }
        container = container.parentElement;
      }

      hideControlNode(labelNode);
      const sibling = labelNode.nextElementSibling;
      if (sibling && (sibling.matches("input, select") || sibling.querySelector("input, select"))) {
        hideControlNode(sibling);
      }
    }

    function hideOAuthClientFields() {
      const nodes = document.querySelectorAll(
        ".swagger-ui .modal-ux-content label, .swagger-ui .modal-ux-content p, .swagger-ui .modal-ux-content span"
      );

      nodes.forEach((node) => {
        if (!isTargetNode(node)) {
          return;
        }
        hideFieldContainer(node);
      });
    }

    function customizeAuthorizationModal() {
      document.querySelectorAll(".swagger-ui .modal-ux-content h4").forEach((heading) => {
        if (normalize(heading.textContent).includes("oauth2password")) {
          heading.textContent = "Вход по логину и паролю";
        }
      });

      document.querySelectorAll(".swagger-ui .modal-ux-content p").forEach((paragraph) => {
        const text = normalize(paragraph.textContent);
        if (
          text.startsWith("scopes are used to grant") ||
          text.startsWith("api requires the following scopes")
        ) {
          paragraph.style.display = "none";
        }
      });
    }

    function preferredTheme() {
      const savedTheme = localStorage.getItem("swagger-theme");
      if (savedTheme === "light" || savedTheme === "dark") {
        return savedTheme;
      }
      return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
    }

    function applyTheme(theme) {
      document.documentElement.dataset.swaggerTheme = theme;
      const toggle = document.getElementById("swagger-theme-toggle");
      if (!toggle) {
        return;
      }

      const isDark = theme === "dark";
      toggle.querySelector(".theme-icon").textContent = isDark ? "☀" : "☾";
      toggle.querySelector(".theme-label").textContent = isDark ? "Светлая" : "Тёмная";
      toggle.setAttribute("aria-label", isDark ? "Включить светлую тему" : "Включить тёмную тему");
      toggle.setAttribute("aria-pressed", String(isDark));
    }

    function setupThemeToggle() {
      const toggle = document.createElement("button");
      toggle.id = "swagger-theme-toggle";
      toggle.type = "button";
      toggle.innerHTML = '<span class="theme-icon" aria-hidden="true"></span>'
        + '<span class="theme-label"></span>';
      toggle.addEventListener("click", function () {
        const nextTheme =
          document.documentElement.dataset.swaggerTheme === "dark" ? "light" : "dark";
        localStorage.setItem("swagger-theme", nextTheme);
        applyTheme(nextTheme);
      });
      document.body.appendChild(toggle);
      applyTheme(preferredTheme());
    }

    applyTheme(preferredTheme());
    setupThemeToggle();

    const observer = new MutationObserver(function () {
      hideOAuthClientFields();
      customizeAuthorizationModal();
    });
    observer.observe(document.body, { childList: true, subtree: true });
    window.addEventListener("load", function () {
      hideOAuthClientFields();
      customizeAuthorizationModal();
    });
    setTimeout(function () {
      hideOAuthClientFields();
      customizeAuthorizationModal();
    }, 300);
  })();
</script>
"""


def _customize_swagger_html(html: str) -> str:
    html = html.replace("</head>", f"{SWAGGER_UI_THEME}</head>")
    return html.replace("</body>", f"{SWAGGER_UI_CUSTOM_SCRIPT}</body>")


def setup_docs_routes(app: FastAPI) -> None:
    @app.get("/docs", include_in_schema=False)
    async def custom_swagger_ui_html() -> HTMLResponse:
        if app.openapi_url is None:
            raise RuntimeError("OpenAPI URL is disabled")
        swagger_ui = get_swagger_ui_html(
            openapi_url=app.openapi_url,
            title=f"{app.title} - Swagger UI",
            oauth2_redirect_url="/docs/oauth2-redirect",
            swagger_ui_parameters={
                "persistAuthorization": True,
                "displayRequestDuration": True,
                "filter": True,
                "defaultModelsExpandDepth": 1,
                "docExpansion": "none",
                "tryItOutEnabled": True,
            },
        )
        return HTMLResponse(_customize_swagger_html(bytes(swagger_ui.body).decode("utf-8")))

    @app.get("/docs/oauth2-redirect", include_in_schema=False)
    async def swagger_ui_redirect() -> HTMLResponse:
        return get_swagger_ui_oauth2_redirect_html()
