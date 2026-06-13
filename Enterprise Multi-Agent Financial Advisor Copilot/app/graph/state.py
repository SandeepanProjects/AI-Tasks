from typing import TypedDict
from typing import Optional
from typing import Dict
from typing import List


class FinancialAdvisorState(TypedDict):

    query: str

    user_id: str

    tenant_id: str

    retrieved_docs: List[str]

    risk_analysis: Optional[str]

    market_research: Optional[str]

    compliance_review: Optional[str]

    final_response: Optional[str]

    metadata: Dict