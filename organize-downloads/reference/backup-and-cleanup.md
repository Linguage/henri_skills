# Cloud backup and subsequent local cleanup

Use this workflow when archiving papers or books to an authorized cloud directory, explaining backup status, or gathering backed-up local files for deletion. Read only the source and destination libraries already in scope.

## Account for every source file

Create a per-file record with the source path, size, local SHA-256 when available, destination path, action, and evidence. Assign one outcome to each source file:

| Outcome | Required explanation |
|---|---|
| Copied and verified in this run | A destination file was created and its content was verified against the source. |
| Already present | Identify the existing destination and the evidence that it contains the same content. Explain that this file was not copied again. |
| Unresolved | Give the concrete gap: unverified candidate, inaccessible content, absent destination, name conflict, or failed copy. Keep the local file. |

A manifest entry, similar title, same name, or equal size alone is not proof of identical content. Prefer matching source/destination content hashes. For offline cloud files, a prior content-verification record tied to the exact destination, together with consistent current path and size, may support the already-present outcome. Record that this relies on historical verification, not a fresh cloud-content hash. If records cannot establish that relationship, leave the file unresolved; do not silently skip it as a duplicate.

An unresolved duplicate candidate is not an archived file. During an authorized backup, if no verified match exists and the approved destination is collision-free, copy the source there and verify it. If a conflict or missing authority prevents that, complete the unaffected copies and identify the precise remaining work; a proposed copy plan is not an executed backup.

Hash-deduplicate copy work when appropriate, but preserve the mapping from each physical source file to its destination. A single archived file may cover several identical local copies. Different formats, editions, translations, and regenerated versions remain distinct unless their content identity is established for the intended operation.

## State what has actually completed

Copying into the local OneDrive folder, verifying that local copy, and completing remote synchronization are different events. Report the verified state; local presence alone does not prove a remote backup. If the user confirms that remote backup has completed, record and use that confirmation without asking the same question again, while retaining the per-file evidence requirement.

At the end of a backup batch, reconcile all source files with the three outcomes above. Report copied files, already-present files, and unresolved files separately. If any file is unresolved, state that the backup is incomplete for those files. Do not describe the entire library as backed up and disclose exclusions only when the user later asks about deletion.

## Execute an authorized cleanup completely

“Backup is complete” supplies backup status; “move what can be cleaned to pending deletion” supplies cleanup authorization. When both are available for the batch, act on them. Do not retain an otherwise eligible file merely because it is the first local copy, called an original, or referenced by an old generated index.

- Recheck the current source files against the evidence and inspect the exact archived destinations without automatically downloading offline publications. Changed or insufficient evidence leaves only the affected files unresolved.
- Put eligible files in one clearly named batch under the agreed `待删除/` directory. Preserve relative library paths to avoid name collisions. Prepare the per-file move list and recovery record, then preflight using `scripts/apply_move_plan.py`; this script checks paths and collisions but does not verify content hashes.
- Compare source sizes and SHA-256 before moving with the resulting files after moving. Verify that the moved source paths are absent and the retained files are unchanged. Stop affected operations on changed files or target collisions; do not overwrite or silently rename.
- Update the affected local catalogs using [phase3-inventory.md](phase3-inventory.md). Remove moved-out entries rather than redirecting them outside the indexed folder. Preserve full-text database bodies and records during this catalog maintenance.
- Keep unresolved publications outside the pending-deletion batch. In a publication-only cleanup, retain database/catalog files separately: a PDF backup does not prove that extracted text, annotations, databases, or management files are backed up. Their cleanup requires its own evidence and inclusion in the authorized scope.
- Remove only confirmed empty directories created or emptied by this batch when that cleanup is in scope; retain library roots and hidden contents. Do not permanently delete the gathered files.

Earlier approval for the same directories and batch remains valid. A user-requested pending-deletion batch does not require another confirmation merely to choose a clear batch name or preserve the files' existing internal directory structure. Material scope changes still require new authority.

## Use counts the user can reconcile

The default unit is one physical publication file, not a unique hash, a database record, or a catalog entry. Count PDF/EPUB pairs as two files and retain distinct versions. State the included file types when the scope is ambiguous. List databases, catalogs, logs, and hidden files separately.

Check these relationships for the same scope and time:

- Files present before this cleanup = files moved in this batch + publication files retained.
- Files present now exclude earlier moved or user-deleted batches. Show a prior batch only when explaining the history, and label it explicitly.
- Copied + already present + unresolved = all source publication files considered for the backup, counting each physical source file once even if several map to one destination.

When resuming, inspect current files and the execution log; do not run an old move plan again or present its old retained count as the current count. If the user has deleted an earlier pending-deletion batch, report it as a previous completed batch rather than part of today's remaining files.

Use direct Chinese such as “目前有 X 份文件；本次移入待删除 Y 份；还剩 Z 份未确认备份的文件，另有 K 个数据库和清单文件”. State the specific reason any file remains. Avoid unexplained labels such as “保留原件”, “去重后的主副本”, or “可回收资料”; they do not tell the user what can be deleted. If comparing two batches, explain their relationship in the same paragraph rather than leaving the user to infer it from several totals.
