# Session backup, readable archiving, and cleanup

Use this workflow to make stored chat history directly readable for recalling previous work, then clean up the selected source sessions after verified backup and authorization. The reading archive must not require the original application or reconstruction of its working state. Do not turn a request to inspect or update a skill into permission to export, upload, or delete user data.

## 1. Establish purpose and scope

Distinguish these goals before choosing an archive format:

| Goal | Preserve | Do not promise |
|---|---|---|
| Resume or restore the original tool state | Original session files, required databases and related state; consistent snapshots | That a transcript alone restores tool history or workspace state |
| Review previous work without restoring it | Full messages, tool operations/results, attachments, chronology and source mapping | Direct import of transformed records into the original app |

When the user only wants to read history, use the readable format below. Do not add a second set of original Base64-heavy records "for safety" without explaining its size and obtaining agreement. If both modes are wanted, report their separate storage costs.

Ask the user to specify an absolute backup path before exporting if no destination has been provided; do not choose a storage provider or personal folder for them. Identify absolute source roots, the selected project, staging location, final destination, retention policy, and authorized removal scope. Keep project files separate from session files. Deleting a session does not undo saved project changes, but can lose results that were never saved elsewhere.

For Codex, inspect both `~/.codex/sessions/` and `~/.codex/archived_sessions/`. Match recorded `session_meta.payload.cwd` or other verified project metadata, not text mentions of a project name. Check historical paths, subdirectories and worktree paths as possible additional scope; report them separately until their relationship and authorization are established. A filename or similarly named directory is not proof of project identity.

Do not infer that an archived session is disposable, that an old session is finished, or that all messages are in one directory. Record unknown/malformed formats and permission failures as unresolved, not as zero usage. For tools other than Codex, inspect actual schemas; do not assume Codex JSONL fields apply.

## 2. Diagnose size before exporting

Build a per-file inventory with relative source path, bytes, SHA-256, project metadata, first/last record timestamps, record counts/types, and user/assistant message counts. Keep active and archived totals separate. Stop or snapshot writers before capture; detect source changes during reading and before removal.

Report:

- Project and month totals, plus the largest files. Directory month usually indicates creation, not the last continuation of a conversation.
- Logical bytes versus allocated disk space. APFS clones, hard links and shared volumes can make directory totals unsuitable as reclaimable-space estimates; note unreadable areas.
- Mutually exclusive record categories: messages, tool outputs, events, compaction records and other state.
- Overlapping measurements, such as embedded-media bytes and repeated outputs, explicitly labeled as overlapping. Do not add them to category totals or promise the sum as savings.

Tool output means the result returned to the assistant by a command, file reader, test runner, image viewer, or other tool. It may contain whole images and structured data, not just terminal text. JSONL can embed `data:image/...;base64,...` inside messages, tool results, event records or serialized JSON strings. Image-generation results may also contain bare encoded image data.

`compacted` is a context-management event, not disk compression. Its replacement/retained histories may store media again and may contain conversation content absent from earlier records, for example after a fork. Inspect and preserve such content instead of discarding all compaction records by type.

Repeated tool results can be measured by content hashes. Repetition alone is not permission to remove occurrences: preserve the original order and each occurrence's reference.

## 3. Build one directly readable archive

For the review-only goal, use a standard ZIP (ZIP64 when necessary) with ordinary files:

```text
<project>_sessions_<first-date>_to_<last-date>_backed-up_<backup-date>.zip
├── README.md
├── index.md
├── sessions/       # Per-session Markdown, ordered messages and tool activity
├── records/        # Plain JSONL/JSON retaining full records with external references
├── assets/         # Deduplicated images and other binary attachments
├── outputs/        # Full long text outputs, referenced rather than summarized
└── manifest.json   # Source mapping, counts, checksums, range, time zone, mode
```

Use the minimum and maximum actual record timestamps in the selected batch, expressed in the user's time zone, for the filename's date range. Include precise range, time zone and backup creation time in the manifest. Do not substitute folder names, modification dates, or the export date for the conversation range.

Preserve full user and assistant messages, tool names/arguments/results, chronological order and references to all associated media. Never replace long outputs with summaries unless the user explicitly accepts that loss. Large text can be an ordinary UTF-8 file linked from the transcript. Handle line endings without silent normalization during content comparisons.

Decode confirmed media encodings to ordinary files and name them by content hash; identical content can share a file across sessions. Preserve each occurrence's link. Do not assume an arbitrary long Base64-looking string is an image: inspect media type/signature, retain unknown content, and preserve encrypted/internal data without trying to decode its meaning.

Inspect nested lists/dictionaries and media contained inside serialized strings. Preserve JSON escaping correctly. In transformed records, document every reference syntax and its target root in README; provide clickable relative attachment/output links in the reading view. Use robust Markdown code fences so a message's own backticks do not break the document.

Keep unknown record types and compaction/retained histories in the plain record archive even if the reading view hides bookkeeping. If original and event records duplicate a message, do not heuristically delete one without a verified identity rule; explain visible duplicates instead.

For "files directly readable after extraction": no nested `.tar.gz`/ZIP, no restoration script requirement, and no custom template archive in place of the records. JSONL with external attachments is readable history, not a byte-identical original rollout. State that distinction.

Do not include both original embedded-image records and extracted images in review-only mode. This can make the ZIP larger than a deduplicated staging archive. Measure the final ZIP itself and inspect compressed size by member category before claiming success. Report staging size, final size and estimated net effect separately.

Build outputs without overwriting unrelated files. Use restricted file permissions and warn about private chats, screenshots, internal URLs and credentials. Do not include authentication files by default; configuration/credential backup needs explicit scope and secure storage. Never print secret values to perform a sensitivity check.

## 4. Verify preservation, not just file counts

Before source removal:

1. Read the completed archive, test integrity, and verify every member's size and SHA-256. Record the ZIP's own SHA-256 separately; a manifest's presence is not evidence that its checksums were checked.
2. Reconcile all selected source files with archive entries. Confirm source/project mapping, record counts, user/assistant counts and record order.
3. For transformed records, resolve text/media references and compare reconstructed record values with the captured source records. Counts alone miss truncation or replacement errors. For original-mode backups, restore to a new scratch directory and compare source bytes/hashes.
4. Verify all exported attachment/output links resolve within the extracted archive and point to valid files. Inspect representative messages, tool calls, large outputs and media; include old/forked and image-heavy conversations when present.
5. Recheck live sources against the capture hashes. Changed, unreadable, malformed or unverified files remain untouched and are explicitly reported.

Use independent expectations from the captured source. Do not derive expected counts solely from the exporter being tested. Record comparison coverage and limits honestly. Never relabel a failed content check as success merely because counts match.

For SQLite-backed tools, use SQLite's backup API or a stopped, consistent snapshot, then run integrity checks on the backup and validate expected content. Do not copy only a live main DB while ignoring its WAL; never independently delete `-wal`/`-shm` files to save space. Opaque Protobuf or encrypted records must remain preserved if a faithful readable export cannot be verified.

## 5. Transfer and cleanup

Use the exact backup path specified by the user, whether it is local, on external storage, or in a synchronized folder. Writing to external or shared storage requires authorization for that destination. Preserve the approved single-package layout; do not create unrelated categories or scan other storage libraries.

Keep these states separate:

| State | Evidence |
|---|---|
| Local ZIP verified | All member checks and package hash passed |
| Copy at the specified backup path verified | Exact destination bytes and hash match the verified ZIP |
| Remote sync complete, if applicable | Reliable provider status or explicit user confirmation; not just local file presence |
| Sources moved out | Reconciliation shows the exact selected source paths are absent |
| Disk space released | Confirmed deletion/eviction or measured allocation change; moving to Trash is not release |

For synchronized destinations, do not claim remote backup completion from a successful local copy; agree whether remote synchronization must finish before source removal. If destination access or verification fails, retain sources and the valid local package, report the blocker, and do not retry a possibly completed non-idempotent move without checking state. Never download unrelated offline content for this workflow.

After the agreed archive verification state is met and removal is authorized, recheck writers and hashes, then move only the selected files to Trash (or the user's agreed pending-deletion location). Check for partial success before any retry. Preserve unrelated sessions, project directories, configurations, skills, generated assets outside the approved batch, worktrees and databases.

Report exact file counts, exclusions, backup mode, archive path/size, source removal state and remote-sync status when applicable. Rescan both active and archived roots for the selected project after cleanup. If a historical alias remains unconfirmed, say so rather than claiming all project history was cleared.

Moving files to Trash does not free their storage. Do not empty the entire Trash to remove one batch; that can destroy unrelated data. If Trash is unreadable, report the last verified action, not an invented current contents or release amount.

Remove only this task's disposable intermediate files after the final archive is verified. Retain an audit/recovery record outside directories being cleaned. A failed or partial task must identify remaining files and the exact next action.

## Conservative tool cleanup

When the user wants tools to remain immediately usable, protect installed environments, current runtimes, project dependencies and browser binaries. Distinguish rebuildable downloads from functional dependencies; reinstalling may require network access.

- **CLI versions:** inspect resolved launchers and running process references. A launcher can point to the latest version while an older process still uses the previous one. Keep both in that case. Inspect executable identity separately from arguments so the agent's own shell/script does not create a false process match.
- **Extensions:** read package identity/version plus `.obsolete`, `extensions.json`, relevant profiles and process references. Multiple directories or an older version number alone do not establish obsolescence. Leave registered, running or uncertain versions in place.
- **Conda:** preview `conda clean --tarballs --index-cache --dry-run --json` for a download-cache-only pass; execute only the approved flags. Do not substitute `--all` or `--force-pkgs-dirs`, remove environments, or manually empty the package directory. Snapshot installed-package metadata and compare after cleanup.
- **npx/Playwright:** deleting cached packages or browser binaries can make an offline task unusable. Skip them when immediate/offline operation is required, unless reinstalling and verifying the needed components is explicitly in scope.
- **Codex:** treat `.tmp`, `tmp`, plugin backups and runtime installation directories independently. Keep active installs, uncertain rollback data and the primary runtime. Leave them untouched while the relevant writer is running unless usage can be safely established.
- **Persistent data:** sessions, archived sessions, snapshots, file-change history, SQLite stores, project worktrees and generated images are not ordinary caches. Apply backup/content verification and scoped approval instead of a blanket cache deletion.

Validate retained CLI launchers, version/startup commands, retained extension files and installed-environment inventories. Exercise relevant runtime imports or a representative local operation where practical. A version command or standard-library import does not establish provider API connectivity or IDE behavior; state the limits and do not launch an unrelated network test.

Report separately: cache allocation actually reduced, obsolete binaries/extensions moved to Trash, protected/in-use items, and functionality checked. Do not promise zero risk, add directory totals as guaranteed savings, or attribute all free-space changes to the cleanup while swap or other processes are changing.
