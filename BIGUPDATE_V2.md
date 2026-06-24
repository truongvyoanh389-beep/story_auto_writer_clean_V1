# Big Update V2

## Baseline

- V1 backup zip has been created before this update.
- V2 starts from the multi-job/profile workflow.

## Goals

- Make Profile Chrome the first operational step.
- Use a job-first workflow: create job, assign free profile, run selected job.
- Keep job state isolated so one job cannot run on multiple profiles by accident.
- Store output under `outputs/<profile>/<project>/`.
- Export story text as `<title>.txt` without title header inside the file.
- Export `seo_meta.txt` with SEO description, hashtags, video tags, and thumbnail prompt.
- Keep thumbnail prompt formula fixed for revenge story competitors:
  - dense text block
  - dark background
  - right-side main character portrait
  - red/yellow bottom punchline
  - white/green/yellow/red text roles

## Immediate Checks

- Verify two jobs can run at the same time only when each has a different assigned profile.
- Verify selecting a job changes Process realtime to that job only.
- Verify tab Nội dung displays the selected job only.
- Verify export auto-runs after a job finishes.
- Verify `seo_meta.txt` is written after export.

## Next Improvements

- Add persistent job queue save/load.
- Add retry controls per failed job.
- Add clearer running/off/busy labels for profiles.
- Add thumbnail preview generation as a separate optional step.
