# """
# Report routes. Wire this into main.py with:
#     from routes.reports import router as reports_router
#     app.include_router(reports_router)
# """
# from fastapi import APIRouter, HTTPException
# from fastapi.responses import HTMLResponse, FileResponse

# from db import scan_runs_col, eval_runs_col, reports_col
# from models.db_schemas import ScanRun, EvalRun, ReportRecord
# from services.report_builder import ReportBuilder

# router = APIRouter(prefix="/agentsec/reports", tags=["reports"])
# builder = ReportBuilder()


# async def _get_scan(scan_id: str) -> ScanRun:
#     doc = await scan_runs_col.find_one({"_id": scan_id})
#     if not doc:
#         raise HTTPException(404, f"scan_id {scan_id} not found")
#     return ScanRun(**doc)


# async def _get_latest_eval(agent_id: str, scan_id: str) -> EvalRun | None:
#     doc = await eval_runs_col.find_one(
#         {"agent_id": agent_id, "scan_id": scan_id},
#         sort=[("run_at", -1)],
#     )
#     if not doc:
#         doc = await eval_runs_col.find_one({"agent_id": agent_id}, sort=[("run_at", -1)])
#     return EvalRun(**doc) if doc else None


# @router.get("/{scan_id}", response_class=HTMLResponse)
# async def get_combined_report(scan_id: str):
#     scan = await _get_scan(scan_id)
#     eval_run = await _get_latest_eval(scan.agent_id, scan_id)

#     html = builder.render_html(scan, eval_run)
#     html_path = builder.save_html(scan_id, html)

#     record = ReportRecord(
#         agent_id=scan.agent_id,
#         scan_id=scan_id,
#         eval_run_id=eval_run.id if eval_run else None,
#         type="COMBINED",
#         html_path=html_path,
#     )
#     await reports_col.update_one(
#         {"scan_id": scan_id, "type": "COMBINED"},
#         {"$set": record.model_dump(by_alias=True)},
#         upsert=True,
#     )
#     return HTMLResponse(content=html)


# @router.get("/{scan_id}/download")
# async def download_pdf(scan_id: str):
#     scan = await _get_scan(scan_id)
#     eval_run = await _get_latest_eval(scan.agent_id, scan_id)
#     html = builder.render_html(scan, eval_run)

#     try:
#         pdf_path = builder.render_pdf(html, scan_id)
#     except ImportError:
#         raise HTTPException(
#             500,
#             "weasyprint not installed — pip install weasyprint --break-system-packages, "
#             "or use the HTML view instead.",
#         )

#     await reports_col.update_one(
#         {"scan_id": scan_id, "type": "COMBINED"},
#         {"$set": {"pdf_path": pdf_path}},
#         upsert=True,
#     )
#     return FileResponse(pdf_path, media_type="application/pdf", filename=f"agentsec_report_{scan_id}.pdf")



# from fastapi import APIRouter, HTTPException
# from fastapi.responses import HTMLResponse, FileResponse

# from core.db import get_db
# from services.report_builder import ReportBuilder

# router = APIRouter(prefix="/agentsec/reports", tags=["reports"])
# builder = ReportBuilder()


# async def _get_scan(scan_id: str) -> dict:
#     db = get_db()
#     doc = await db.scan_reports.find_one({"scan_id": scan_id})
#     if not doc:
#         raise HTTPException(404, f"scan_id {scan_id} not found in scan_reports")
#     return doc


# async def _get_latest_eval(agent_id: str, scan_id: str) -> dict | None:
#     db = get_db()
#     doc = await db.eval_results.find_one(
#         {"agent_id": agent_id, "scan_id": scan_id},
#         sort=[("run_at", -1)],
#     )
#     if not doc:
#         doc = await db.eval_results.find_one({"agent_id": agent_id}, sort=[("run_at", -1)])
#     return doc


# @router.get("/{scan_id}", response_class=HTMLResponse)
# async def get_combined_report(scan_id: str):
#     scan_doc = await _get_scan(scan_id)
#     agent_id = scan_doc.get("agent_id")
#     eval_doc = await _get_latest_eval(agent_id, scan_id)

#     html = builder.render_html(scan_doc, eval_doc)
#     builder.save_html(scan_id, html)
#     return HTMLResponse(content=html)


# @router.get("/{scan_id}/json")
# async def get_combined_report_json(scan_id: str):
#     """JSON version of the combined report, for the frontend report page."""
#     scan_doc = await _get_scan(scan_id)
#     scan_doc.pop("_id", None)

#     agent_id = scan_doc.get("agent_id")
#     eval_doc = await _get_latest_eval(agent_id, scan_id)
#     if eval_doc:
#         eval_doc.pop("_id", None)

#     return {"status": "completed", "report": scan_doc}


# @router.get("/{scan_id}/download")
# async def download_pdf(scan_id: str):
#     scan_doc = await _get_scan(scan_id)
#     agent_id = scan_doc.get("agent_id")
#     eval_doc = await _get_latest_eval(agent_id, scan_id)
#     html = builder.render_html(scan_doc, eval_doc)

#     try:
#         pdf_path = builder.render_pdf(html, scan_id)
#     except ImportError:
#         raise HTTPException(500, "weasyprint not installed")
#     except RuntimeError as e:
#         raise HTTPException(503, str(e))

#     return FileResponse(pdf_path, media_type="application/pdf", filename=f"agentsec_report_{scan_id}.pdf")

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import HTMLResponse, FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import get_db
from services.report_builder import ReportBuilder

from auth import get_current_user
from models.sql_models import User
from database import get_db as get_pg_db
from services.ownership_service import user_owns_scan

router = APIRouter(prefix="/agentsec/reports", tags=["reports"])
builder = ReportBuilder()


async def _get_scan(scan_id: str) -> dict:
    db = get_db()
    doc = await db.scan_reports.find_one({"scan_id": scan_id})
    if not doc:
        raise HTTPException(404, f"scan_id {scan_id} not found in scan_reports")
    return doc


async def _get_latest_eval(agent_id: str, scan_id: str) -> dict | None:
    db = get_db()
    doc = await db.eval_results.find_one(
        {"agent_id": agent_id, "scan_id": scan_id}, sort=[("run_at", -1)],
    )
    if not doc:
        doc = await db.eval_results.find_one({"agent_id": agent_id}, sort=[("run_at", -1)])
    return doc


async def _check_ownership(scan_id: str, current_user: User, pg_db: AsyncSession):
    if not await user_owns_scan(pg_db, scan_id, current_user.org_id):
        raise HTTPException(status_code=403, detail="Access denied to this report")


@router.get("/{scan_id}", response_class=HTMLResponse)
async def get_combined_report(
    scan_id: str,
    current_user: User = Depends(get_current_user),
    pg_db: AsyncSession = Depends(get_pg_db),
):
    await _check_ownership(scan_id, current_user, pg_db)
    scan_doc = await _get_scan(scan_id)
    agent_id = scan_doc.get("agent_id")
    eval_doc = await _get_latest_eval(agent_id, scan_id)
    html = builder.render_html(scan_doc, eval_doc)
    builder.save_html(scan_id, html)
    return HTMLResponse(content=html)


@router.get("/{scan_id}/json")
async def get_combined_report_json(
    scan_id: str,
    current_user: User = Depends(get_current_user),
    pg_db: AsyncSession = Depends(get_pg_db),
):
    await _check_ownership(scan_id, current_user, pg_db)
    scan_doc = await _get_scan(scan_id)
    scan_doc.pop("_id", None)
    agent_id = scan_doc.get("agent_id")
    eval_doc = await _get_latest_eval(agent_id, scan_id)
    if eval_doc:
        eval_doc.pop("_id", None)
    return {"status": "completed", "report": scan_doc}


@router.get("/{scan_id}/download")
async def download_pdf(
    scan_id: str,
    current_user: User = Depends(get_current_user),
    pg_db: AsyncSession = Depends(get_pg_db),
):
    await _check_ownership(scan_id, current_user, pg_db)
    scan_doc = await _get_scan(scan_id)
    agent_id = scan_doc.get("agent_id")
    eval_doc = await _get_latest_eval(agent_id, scan_id)
    html = builder.render_html(scan_doc, eval_doc)
    try:
        pdf_path = builder.render_pdf(html, scan_id)
    except ImportError:
        raise HTTPException(500, "weasyprint not installed")
    except RuntimeError as e:
        raise HTTPException(503, str(e))
    return FileResponse(pdf_path, media_type="application/pdf", filename=f"agentsec_report_{scan_id}.pdf")