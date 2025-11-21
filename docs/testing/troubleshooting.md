# Troubleshooting Matrix

| Symptom | Likely Cause | Where to Check | Fix |
| --- | --- | --- | --- |
| Extraction fails (500/422) | Invalid image URL/base64, missing API key | API logs, request payload | Validate URL/base64, set `ANTHROPIC_API_KEY`, retry |
| CORS errors in browser | Missing/incorrect CORS config | Browser console, API headers | Update CORS allowlist/origins |
| Empty exports | Library/session missing tokens | `/sessions/{id}/library`, DB `color_tokens.library_id` | Run batch extract, ensure persist, then export |
| DB errors / migration mismatch | Alembic not applied | API logs, DB schema | `alembic upgrade head` |
| Frontend cannot reach API | Proxy/base URL wrong | Vite proxy config, network tab | Update API base URL/proxy target |
| Slow batch extraction | Overly high `max_colors` or low Delta-E | API logs, request params | Reduce `max_colors`, adjust `delta_e_threshold`, tune concurrency |
| Roles not applied | Curation not run or invalid roles | Curation request, DB `role` column | Re-run curation with valid roles |
| Unexpected token counts | Dedup threshold too strict/lenient | Aggregation settings | Adjust `delta_e_threshold`, inspect provenance |
