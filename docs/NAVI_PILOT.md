# NAVI pilot
This complementary gate uses profile python-tooling. Scope: Local administrative policy unit tests; no administrative script execution or host config installation.
Core SHA: e9fa2e4c825615ddc6f0a24b65d7139ec38fc477. Read-only workflow token, no inherited secrets, no
private export. No original workflow or application code changed. A passing
gate is not production certification. Merge only after reviewed Core and
pilot gates, actual restore-tested backup and rollout approval. Rollback:
revert the integration commit. No automatic merge or ruleset changes.


Validated release candidate: NAVI Core v0.2.0rc1 (signed wheel and Linux/Windows install). Complementary verification only; existing CI, branch governance and production approval remain unchanged. Rollback: revert this integration commit.
