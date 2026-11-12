"""LangChain chat-model factory for Amazon Bedrock Converse API."""
from app.config import settings


def create_bedrock_chat_model():
    try:
        from langchain_aws import ChatBedrockConverse
    except ImportError as exc:  # pragma: no cover - optional dependency
        raise RuntimeError("Bedrock chat requires the AWS extra: pip install -e '.[aws]'") from exc
    return ChatBedrockConverse(
        model=settings.aws_bedrock_chat_model_id,
        region_name=settings.aws_region,
        temperature=0,
        max_tokens=settings.aws_bedrock_max_tokens,
    )
