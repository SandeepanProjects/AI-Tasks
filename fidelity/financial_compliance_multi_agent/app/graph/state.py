from typing import TypedDict, Any
class ComplianceState(TypedDict,total=False):
    review_id:str; tenant_id:str; content:str; db:Any; claims:list[dict]; research:dict; analysis:dict; result:dict
