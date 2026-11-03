from fastapi import APIRouter, Depends, HTTPException
import httpx
from app.application.schemas import EvidenceIngestRequest, EvidenceIngestResponse
from app.core.security import Principal, Role, require_role
from app.core.errors import DomainError
from app.db.session import get_session
from app.adapters.repositories import SqlEvidenceIngestionRepository
from app.adapters.embeddings import build_embedding_provider
from app.application.ingestion import EvidenceIngestionService

router = APIRouter(prefix="/evidence", tags=["evidence"])

@router.post("/ingest", response_model=EvidenceIngestResponse, status_code=201)
async def ingest_evidence(body: EvidenceIngestRequest,
    principal: Principal = Depends(require_role(Role.ADMIN)), session=Depends(get_session)):
    try:
        service = EvidenceIngestionService(SqlEvidenceIngestionRepository(session), build_embedding_provider())
        count = await service.ingest(tenant_id=principal.tenant_id, source_name=body.source_name,
            source_uri=body.source_uri, content=body.content, metadata=body.metadata)
        return EvidenceIngestResponse(chunks_created=count)
    except ValueError as exc:
        raise HTTPException(422, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(503, detail="Embedding provider is not configured") from exc
    except httpx.HTTPError as exc:
        raise HTTPException(503, detail="Embedding provider unavailable") from exc
    except DomainError as exc:
        raise HTTPException(exc.status_code, detail={"code": exc.code, "message": str(exc)}) from exc
