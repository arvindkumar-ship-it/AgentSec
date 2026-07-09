# """
# ReportBuilder: takes a scan document + optional eval document, produces a view-model,
# renders combined_report.html via Jinja2, and optionally converts to PDF.
# """
# import os
# from typing import Optional
# from jinja2 import Environment, FileSystemLoader, select_autoescape

# TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "..", "templates")
# OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "generated_reports")
# os.makedirs(OUTPUT_DIR, exist_ok=True)

# _env = Environment(
#     loader=FileSystemLoader(TEMPLATE_DIR),
#     autoescape=select_autoescape(["html"]),
# )


# class ReportBuilder:

#     def build_view_model(self, scan_doc: dict, eval_doc: Optional[dict]) -> dict:
#         r = scan_doc
#         e = eval_doc

#         return {
#             "metadata": {
#                 "agent_name": r.get("agent_name"),
#                 "agent_id": r.get("agent_id"),
#                 "scan_id": r.get("scan_id"),
#                 "scan_type": r.get("scan_type"),
#                 "generated_at": r.get("generated_at"),
#                 "dynamic_testing_performed": r.get("dynamic_testing_performed"),
#             },
#             "executive_summary": {
#                 "risk_level": r.get("risk_level"),
#                 "security_score": r.get("security_score"),
#                 "text": r.get("executive_summary"),
#             },
#             "statistics": r.get("statistics", {}),
#             "static_findings": r.get("static_findings", []),
#             "successful_attacks": r.get("successful_attacks", []),
#             "needs_review_attacks": r.get("needs_review_attacks", []),
#             "top_fixes": r.get("top_fixes", []),
#             "raw_results": r.get("raw_results", []),
#             "extra_modules": {
#                 "multiturn_attacks": r.get("multiturn_attacks"),
#                 "document_injection": r.get("document_injection"),
#                 "blackbox_probes": r.get("blackbox_probes"),
#                 "execution_errors": r.get("execution_errors"),
#             },
#             "eval": e,
#             "eval_metrics": self._extract_eval_metrics(e),
#         }

#     def _extract_eval_metrics(self, e: Optional[dict]) -> Optional[dict]:
#         if not e:
#             return None
#         cb = e.get("category_breakdown", {})
#         return {
#             "pass_rate": e.get("pass_rate"),
#             "total_tests": e.get("total_tests"),
#             "successful_attacks": e.get("successful_attacks"),
#             "execution_errors": e.get("execution_errors"),
#             "prompt_injection": cb.get("prompt_injection"),
#             "insecure_output": cb.get("insecure_output"),
#             "data_exfiltration": cb.get("data_exfiltration"),
#             "note": e.get("note"),
#         }

#     def render_html(self, scan_doc: dict, eval_doc: Optional[dict]) -> str:
#         vm = self.build_view_model(scan_doc, eval_doc)
#         template = _env.get_template("combined_report.html")
#         return template.render(**vm)

#     def save_html(self, scan_id: str, html: str) -> str:
#         path = os.path.join(OUTPUT_DIR, f"{scan_id}.html")
#         with open(path, "w", encoding="utf-8") as f:
#             f.write(html)
#         return path

#     def render_pdf(self, html: str, scan_id: str) -> str:
#         """
#         Requires `weasyprint`. On Render add to requirements.txt AND
#         add an apt buildpack/aptfile with: libpango-1.0-0 libpangocairo-1.0-0
#         libgdk-pixbuf2.0-0 libffi-dev. If that's too heavy for your deploy,
#         skip PDF entirely and just serve HTML — most users just view it.
#         """
#         from weasyprint import HTML  # imported lazily so HTML-only path never needs it
#         pdf_path = os.path.join(OUTPUT_DIR, f"{scan_id}.pdf")
#         HTML(string=html).write_pdf(pdf_path)
#         return pdf_path









"""
ReportBuilder: takes a scan document + optional eval document, produces a view-model,
renders combined_report.html via Jinja2, and optionally converts to PDF.
"""
import os
from typing import Optional
from jinja2 import Environment, FileSystemLoader, select_autoescape

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "..", "templates")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "generated_reports")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Local Windows dev only: MSYS2/GTK bin dir for WeasyPrint's native libraries.
# Ignored on Linux (Render) — there, apt-installed libs are already on the system path.
_WINDOWS_GTK_BIN = r"D:\msys64\ucrt64\bin"

_env = Environment(
    loader=FileSystemLoader(TEMPLATE_DIR),
    autoescape=select_autoescape(["html"]),
)


class ReportBuilder:

    def build_view_model(self, scan_doc: dict, eval_doc: Optional[dict]) -> dict:
        r = scan_doc
        e = eval_doc

        return {
            "metadata": {
                "agent_name": r.get("agent_name"),
                "agent_id": r.get("agent_id"),
                "scan_id": r.get("scan_id"),
                "scan_type": r.get("scan_type"),
                "generated_at": r.get("generated_at"),
                "dynamic_testing_performed": r.get("dynamic_testing_performed"),
            },
            "executive_summary": {
                "risk_level": r.get("risk_level"),
                "security_score": r.get("security_score"),
                "text": r.get("executive_summary"),
            },
            "statistics": r.get("statistics", {}),
            "static_findings": r.get("static_findings", []),
            "successful_attacks": r.get("successful_attacks", []),
            "needs_review_attacks": r.get("needs_review_attacks", []),
            "top_fixes": r.get("top_fixes", []),
            "raw_results": r.get("raw_results", []),
            "extra_modules": {
                "multiturn_attacks": r.get("multiturn_attacks"),
                "document_injection": r.get("document_injection"),
                "blackbox_probes": r.get("blackbox_probes"),
                "execution_errors": r.get("execution_errors"),
            },
            "eval": e,
            "eval_metrics": self._extract_eval_metrics(e),
        }

    def _extract_eval_metrics(self, e: Optional[dict]) -> Optional[dict]:
        if not e:
            return None
        cb = e.get("category_breakdown", {})
        return {
            "pass_rate": e.get("pass_rate"),
            "total_tests": e.get("total_tests"),
            "successful_attacks": e.get("successful_attacks"),
            "execution_errors": e.get("execution_errors"),
            "prompt_injection": cb.get("prompt_injection"),
            "insecure_output": cb.get("insecure_output"),
            "data_exfiltration": cb.get("data_exfiltration"),
            "note": e.get("note"),
        }

    def render_html(self, scan_doc: dict, eval_doc: Optional[dict]) -> str:
        vm = self.build_view_model(scan_doc, eval_doc)
        template = _env.get_template("combined_report.html")
        return template.render(**vm)

    def save_html(self, scan_id: str, html: str) -> str:
        path = os.path.join(OUTPUT_DIR, f"{scan_id}.html")
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        return path

    def render_pdf(self, html: str, scan_id: str) -> str:
        """
        Requires `weasyprint`. On Render add to requirements.txt AND
        add an apt buildpack/aptfile with: libpango-1.0-0 libpangocairo-1.0-0
        libgdk-pixbuf2.0-0 libffi-dev.

        On Windows, WeasyPrint's native GTK libraries (installed via MSYS2)
        aren't always discoverable automatically — explicitly register the
        DLL directory before import. No-op on Linux/macOS.
        """
        if os.name == "nt" and os.path.isdir(_WINDOWS_GTK_BIN):
            os.add_dll_directory(_WINDOWS_GTK_BIN)

        try:
            from weasyprint import HTML  # imported lazily so HTML-only path never needs it
        except OSError as e:
            raise RuntimeError(
                "PDF export unavailable: WeasyPrint's native libraries (GTK/Pango) "
                "could not be loaded. View the HTML report instead, or check the "
                "WeasyPrint installation."
            ) from e

        pdf_path = os.path.join(OUTPUT_DIR, f"{scan_id}.pdf")
        HTML(string=html).write_pdf(pdf_path)
        return pdf_path