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
    --bg: #f6f8fb;
    --surface: #fff;
    --text: #18212f;
    --muted-text: #526173;
    --border: #64748b;
  }
  html[data-swagger-theme="dark"] {
    color-scheme: dark;
    --bg: #0b1120;
    --surface: #111827;
    --text: #e5edf7;
    --muted-text: #b8c5d6;
  }
  body, .swagger-ui { background: var(--bg); color: var(--text); }
  .swagger-ui .info .title, .swagger-ui .info p, .swagger-ui .opblock-tag,
  .swagger-ui .model-title, .swagger-ui .model, .swagger-ui label {
    color: var(--text);
  }
  .swagger-ui .opblock-tag small,
  .swagger-ui .opblock .opblock-summary-path,
  .swagger-ui .opblock .opblock-summary-path__deprecated,
  .swagger-ui .opblock .opblock-summary-description {
    color: var(--muted-text);
  }
  html[data-swagger-theme="dark"] .swagger-ui .opblock-control-arrow svg,
  html[data-swagger-theme="dark"] .swagger-ui .expand-operation svg,
  html[data-swagger-theme="dark"] .swagger-ui .models-control svg,
  html[data-swagger-theme="dark"] .swagger-ui .model-toggle::after {
    fill: var(--text);
  }
  html[data-swagger-theme="dark"] .swagger-ui .markdown p,
  html[data-swagger-theme="dark"] .swagger-ui .renderedMarkdown p,
  html[data-swagger-theme="dark"] .swagger-ui .opblock-description-wrapper p,
  html[data-swagger-theme="dark"] .swagger-ui .opblock-external-docs-wrapper p,
  html[data-swagger-theme="dark"] .swagger-ui .opblock-title_normal p,
  html[data-swagger-theme="dark"] .swagger-ui .parameter__name,
  html[data-swagger-theme="dark"] .swagger-ui .parameter__type,
  html[data-swagger-theme="dark"] .swagger-ui .response-col_status,
  html[data-swagger-theme="dark"] .swagger-ui .response-col_links,
  html[data-swagger-theme="dark"] .swagger-ui .responses-inner h4,
  html[data-swagger-theme="dark"] .swagger-ui .responses-inner h5,
  html[data-swagger-theme="dark"] .swagger-ui table thead tr td,
  html[data-swagger-theme="dark"] .swagger-ui table thead tr th,
  html[data-swagger-theme="dark"] .swagger-ui .tab li {
    color: var(--text);
  }
  .swagger-ui .scheme-container, .swagger-ui section.models,
  .swagger-ui .model-container, .swagger-ui .opblock .opblock-section-header {
    background: var(--surface); color: var(--text); border-color: var(--border);
  }
  #swagger-theme-toggle { position: fixed; z-index: 10000; top: 14px; right: 18px;
    height: 38px; padding: 0 14px; border: 1px solid var(--border); border-radius: 999px;
    background: var(--surface); color: var(--text); cursor: pointer; }
</style>
<script>
  (function () {
    function apply(theme) {
      document.documentElement.dataset.swaggerTheme = theme;
      const button = document.getElementById("swagger-theme-toggle");
      if (button) button.textContent = theme === "dark" ? "Светлая" : "Тёмная";
    }
    const saved = localStorage.getItem("swagger-theme");
    const preferred = window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
    apply(saved || preferred);
    window.addEventListener("load", function () {
      const button = document.createElement("button");
      button.id = "swagger-theme-toggle";
      button.type = "button";
      button.onclick = function () {
        const next = document.documentElement.dataset.swaggerTheme === "dark" ? "light" : "dark";
        localStorage.setItem("swagger-theme", next);
        apply(next);
      };
      document.body.appendChild(button);
      apply(document.documentElement.dataset.swaggerTheme);
    });
  })();
</script>
"""


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
        html = (
            bytes(swagger_ui.body).decode("utf-8").replace("</body>", f"{SWAGGER_UI_THEME}</body>")
        )
        return HTMLResponse(html)

    @app.get("/docs/oauth2-redirect", include_in_schema=False)
    async def swagger_ui_redirect() -> HTMLResponse:
        return get_swagger_ui_oauth2_redirect_html()
