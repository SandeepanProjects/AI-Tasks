def test_shared_packages_import():
    import platform_core, platform_auth, platform_db, platform_cache
    import platform_messaging, platform_observability
    import ai_llm, ai_rag, ai_agents, ai_guardrails
    assert all([
        platform_core, platform_auth, platform_db, platform_cache,
        platform_messaging, platform_observability,
        ai_llm, ai_rag, ai_agents, ai_guardrails,
    ])
