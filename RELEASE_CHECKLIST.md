# Release Checklist

Do not create a remote repo, push, deploy, or post publicly until explicit maintainer approval.

- [ ] Examples are synthetic only.
- [ ] No private data is present.
- [ ] No client, employer, recruiter, school, family, personal, or private data is present.
- [ ] No Unit27 suite numbering is added.
- [ ] No job-search or legacy project material is present.
- [ ] MIT `LICENSE` is present.
- [ ] GitHub Actions CI workflow is present at `.github/workflows/ci.yml`.
- [ ] Review-only outputs are regenerated.
- [ ] Generated outputs contain source line, match basis, artifact date, artifact age, freshness window, `proof_decay`, `stale_artifact`, risk flags, and boundary notes.
- [ ] Tests pass: `python3 -m unittest discover -s tests`.
- [ ] Compile check passes: `PYTHONPYCACHEPREFIX=/private/tmp/proof_decay_pycache python3 -m py_compile proof_decay.py run.py`.
- [ ] CI demo checks cover review-only output and absence of generated rewrite sections.
- [ ] Public copy does not claim truth verification, fraud prevention, certification, production readiness, or guaranteed detection.
- [ ] Explicit maintainer approval is given before remote repo creation, push, deploy, or public post.
