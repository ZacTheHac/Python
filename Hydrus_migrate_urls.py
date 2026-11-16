import argparse
import re
import json
import sys
from datetime import datetime
from urllib.parse import urlparse
from decimal import Decimal, ROUND_HALF_UP
import requests #needs to be installed - pip install requests

#Example usage:
"""
python hydrus_migrate_urls.py \
  --api-key "YOUR_64_CHAR_KEY" \
  --old-domain "https://oldsite.com" \
  --new-domain "newsite.org" \
  --mode add \
  --dry-run
"""
#practical example: --regex --old-domain "(?P<baddomain>^https?://*DOMAIN*\.net/(posts/)?-)(?P<https>https?:/)(/)?(?P<origurl>.*$)" --new-domain "\g<https>/\g<origurl>"
	#this will try to find all the URLs that were originally mis-parsed as "http:/domain.net", leading to the saved URL instead being "http://Sourcedomain.net/https:/domain.net"

def looks_like_regex(pattern: str) -> str:
	"""
	Inspects the input string to determine if it is a standard domain/URL or a regex.
	Returns 'domain', 'regex', or 'unsure'.
	"""
	cleaned = pattern.strip()
	if not cleaned:
		return "domain"

	# Strip valid URL scheme prefix before checking characters
	without_scheme = re.sub(r"^https?://", "", cleaned, flags=re.IGNORECASE)

	# Characters/constructs that are invalid in standard URLs and strongly indicate regex
	# (anchors ^, angle brackets < > for named groups/lookbehinds, curly braces { },
	# pipes |, backslashes \, parentheses ( ), or + outside of query strings)
	unambiguous_regex_chars = r"[\^\<\>\{\}\|\\\(\)]"
	if re.search(unambiguous_regex_chars, without_scheme):
		return "regex"

	# A colon is valid only when followed by digits for a port (e.g., ://example.com:4199...)
	# Colons elsewhere (like (?P:...) or unstripped schemes) indicate regex or ambiguity
	without_valid_port = re.sub(r":\d+(?=/|$)", "", without_scheme, count=1)
	if ":" in without_valid_port:
		return "regex"

	# Characters valid in some URLs (query strings, array params, etc.) but also common in regex
	ambiguous_chars = r"[\?\$\[\]\+\*]"
	if re.search(ambiguous_chars, without_scheme):
		return "unsure"

	# Check if it parses cleanly as a plain domain with no path
	sanitized = sanitize_domain(cleaned)
	if sanitized and "." in sanitized and not re.search(r"[^a-z0-9.\-:]", sanitized):
		parsed = urlparse(cleaned if "://" in cleaned else "http://" + cleaned)
		if parsed.path and parsed.path != "/":
			return "unsure"
		return "domain"

	return "unsure"



def transform_url(url: str, old_pattern: str, new_pattern: str, use_regex: bool, compiled_regex: re.Pattern | None = None) -> str | None:
	"""Transforms a URL using either compiled regex substitution or strict host domain replacement."""
	if use_regex and compiled_regex is not None:
		if compiled_regex.search(url):
			new_url = compiled_regex.sub(new_pattern, url)
			return new_url if new_url != url else None
		return None
	return swap_url_domain(url, old_pattern, new_pattern)


def round_half_up(value: float) -> int:
	"""Rounds a float to the nearest whole number using standard half-up rounding."""
	return int(Decimal(str(value)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def sanitize_domain(raw_input: str) -> str:
	"""Extracts and normalizes the domain/netloc from any URL or domain string."""
	cleaned = raw_input.strip()
	if not cleaned:
		return ""
	if "://" not in cleaned:
		cleaned = "http://" + cleaned
	parsed = urlparse(cleaned)
	# Return netloc (domain + optional port), lowercased, without trailing slashes
	domain = parsed.netloc.lower().rstrip("/")
	return domain


def parse_args():
	parser = argparse.ArgumentParser(
		description="Migrate or add known URLs in Hydrus Network from an old domain to a new domain."
	)
	parser.add_argument(
		"--api-url",
		default="http://127.0.0.1:45869",
		help="Hydrus Client API URL (default: http://127.0.0.1:45869)",
	)
	parser.add_argument(
		"--api-key",
		help="64-character Hydrus Client API access key",
	)
	parser.add_argument(
		"--old-domain",
		help="Old domain to search for (e.g., oldsite.com, https://oldsite.com, or a regex pattern)",
	)
	parser.add_argument(
		"--new-domain",
		help="New domain to migrate to (e.g., newsite.com, https://newsite.com, or a regex substitution)",
	)
	match_group = parser.add_mutually_exclusive_group()
	match_group.add_argument(
		"--regex",
		action="store_true",
		help="Force treating old-domain as a regular expression and new-domain as a substitution pattern",
	)
	match_group.add_argument(
		"--domain",
		action="store_true",
		help="Force standard domain replacement even if the input looks like a regular expression",
	)

	parser.add_argument(
		"--mode",
		choices=["add", "replace"],
		help="Whether to ADD the new URL alongside the old one, or REPLACE (delete) the old URL",
	)
	parser.add_argument(
		"--dry-run",
		action="store_true",
		help="Simulate the migration and generate the log without modifying Hydrus",
	)
	parser.add_argument(
		"--log-file",
		help="Custom path for the JSON output log file (default: auto-generated timestamped file)",
	)
	parser.add_argument(
		"--batch-size",
		type=int,
		default=500,
		help="Number of files to fetch metadata for per API call (default: 500)",
	)
	parser.add_argument(
		"--rollback",
		metavar="LOG_FILE",
		help="Path to a live migration JSON log file to revert/undo",
	)

	return parser.parse_args()


def get_interactive_inputs(args):
	"""Prompts the user for any options not passed via CLI flags."""
	api_key = args.api_key
	while not api_key:
		print("An API key can get gotten in Hydrus under 'services -> review services -> local -> client api'")
		api_key = input("Enter your Hydrus Client API Access Key: ").strip()

	raw_old = args.old_domain.strip() if args.old_domain else ""
	while not raw_old:
		raw_old = input("Enter the OLD domain or regex pattern (e.g., olddomain.com or ^https?://old\\.com): ").strip()

		# Determine whether to use regex mode
	if args.regex:
		use_regex = True
	elif args.domain:
		use_regex = False
	else:
		use_regex = False #default to domain mode
		detection = looks_like_regex(raw_old)
		if detection == "regex":
			print("Detected regular expression syntax in OLD pattern — enabling REGEX mode.")
			use_regex = True
		elif detection == "unsure":
			rx_choice = input("Input could be a standard domain or a regex/path pattern. Use REGEX mode? [Y/N]: ").strip().lower()
			use_regex = rx_choice in ("y", "yes", "regex")


	if use_regex:
		old_pattern = raw_old
		new_pattern = args.new_domain.strip() if args.new_domain else ""
		while not new_pattern:
			new_pattern = input("Enter the NEW regex substitution string (e.g., https://newdomain.com\\1): ").strip()
	else:
		old_pattern = sanitize_domain(raw_old)
		while not old_pattern:
			raw_old = input("Invalid domain. Enter the OLD domain (e.g., olddomain.com): ").strip()
			old_pattern = sanitize_domain(raw_old)

		new_pattern = sanitize_domain(args.new_domain) if args.new_domain else ""
		while not new_pattern:
			raw_new = input("Enter the NEW domain (e.g., newdomain.com or https://newdomain.com): ").strip()
			new_pattern = sanitize_domain(raw_new)

	mode = args.mode
	while mode not in ("add", "replace"):
		choice = input("Mode - [A]DD new URLs alongside old ones, or [R]EPLACE (delete) old URLs? (a/r): ").strip().lower()
		if choice in ("a", "add"):
			mode = "add"
		elif choice in ("r", "rep", "replace", "del", "delete"):
			mode = "replace"

	dry_run = args.dry_run
	# If mode/domains were entered interactively and --dry-run wasn't explicitly passed on CLI, ask about dry run
	if not args.dry_run and not (args.old_domain and args.new_domain and args.mode):
		dr_choice = input("Perform a DRY RUN first? (no changes will be sent to Hydrus) [Y/N]: ").strip().lower()
		dry_run = dr_choice in ("", "y", "yes", "dry", "dryrun")

	return api_key, old_pattern, new_pattern, mode, dry_run, use_regex



def swap_url_domain(url: str, old_domain: str, new_domain: str) -> str | None:
	"""
	Replaces old_domain with new_domain strictly in the host/netloc portion of the URL
	so path segments or query parameters aren't accidentally altered.
	"""
	try:
		parsed = urlparse(url)
		netloc_lower = parsed.netloc.lower()
		if netloc_lower == old_domain or netloc_lower.endswith("." + old_domain):
			# Preserve any subdomain (e.g., static.olddomain.com -> static.newdomain.com)
			if netloc_lower == old_domain:
				new_netloc = new_domain
			else:
				subdomain = parsed.netloc[: -(len(old_domain) + 1)]
				new_netloc = f"{subdomain}.{new_domain}"
			return parsed._replace(netloc=new_netloc).geturl()
	except Exception:
		pass
	return None

def execute_live_changes(api_url: str, headers: dict, planned_files: list, old_domain: str, new_domain: str, mode: str, candidate_count: int, log_filename: str):
	"""Applies the pre-calculated file URL updates to Hydrus and writes a live execution log."""
	print("\n--- Executing Live Migration ---")
	live_log_data = {
		"timestamp": datetime.now().isoformat(),
		"dry_run": False,
		"old_domain": old_domain,
		"new_domain": new_domain,
		"mode": mode,
		"summary": {
			"candidate_files_found": candidate_count,
			"files_modified": 0,
			"total_urls_added": 0,
			"total_urls_removed": 0,
			"errors": 0,
		},
		"files": [],
	}

	for entry in planned_files:
		file_hash = entry["hash"]
		urls_to_add = entry["urls_added"]
		urls_to_delete = entry["urls_removed"]

		live_entry = {
			"hash": file_hash,
			"action": "applied",
			"urls_added": urls_to_add,
			"urls_removed": urls_to_delete,
		}
		if "replaced_pairs" in entry:
			live_entry["replaced_pairs"] = entry["replaced_pairs"]

		payload = {
			"hash": file_hash,
			"urls_to_add": urls_to_add,
			"urls_to_delete": urls_to_delete,
		}

		try:
			post_res = requests.post(
				f"{api_url}/add_urls/associate_url",
				headers=headers,
				json=payload,
			)
			if not post_res.ok:
				raise requests.HTTPError(f"{post_res.status_code}: {post_res.text}")
		except requests.RequestException as e:
			live_entry["action"] = "error"
			live_entry["error"] = str(e)
			live_log_data["summary"]["errors"] += 1
			print(f"[ERROR] Failed updating {file_hash}: {e}")

		live_log_data["files"].append(live_entry)
		if live_entry["action"] != "error":
			live_log_data["summary"]["files_modified"] += 1
			live_log_data["summary"]["total_urls_added"] += len(urls_to_add)
			live_log_data["summary"]["total_urls_removed"] += len(urls_to_delete)
			print(f"[UPDATED] {file_hash} | +{len(urls_to_add)} added, -{len(urls_to_delete)} removed")

	with open(log_filename, "w", encoding="utf-8") as f:
		json.dump(live_log_data, f, indent=2)

	print("\n--- Live Run Summary ---")
	print(f"Files modified        : {live_log_data['summary']['files_modified']}")
	print(f"URLs added            : {live_log_data['summary']['total_urls_added']}")
	print(f"URLs removed          : {live_log_data['summary']['total_urls_removed']}")
	if live_log_data["summary"]["errors"]:
		print(f"Errors encountered    : {live_log_data['summary']['errors']}")
	print(f"Live log saved to     : {log_filename}")

def verify_api_permissions(api_url: str, headers: dict, require_search: bool, require_edit: bool) -> bool:
	"""Connects to Hydrus API and verifies required permissions. Returns whether editing URLs is permitted. Exits if critical errors found."""
	# 1. Verify API connection and required permissions
	try:
		verify_res = requests.get(f"{api_url}/verify_access_key", headers=headers, timeout=10)
		verify_res.raise_for_status()
		verify_data = verify_res.json()
	except requests.RequestException as e:
		print(f"Error connecting to Hydrus Client API: {e}")
		sys.exit(1)

	permits_everything = verify_data.get("permits_everything", False)
	basic_permissions = verify_data.get("basic_permissions", [])
	can_edit_urls = permits_everything or (0 in basic_permissions)

	if not permits_everything:
		missing_perms = []
		if require_search and 3 not in basic_permissions:
			missing_perms.append("Search for and Fetch Files (ID 3)")
		if require_edit and not can_edit_urls:
			missing_perms.append("Import and Edit URLs (ID 0)")
		elif not can_edit_urls:
			print("Warning: your current API key cannot write back URLs. This is okay right NOW because this is a dry run, but it will error if you try to do a real run.")

		if missing_perms:
			print("Error: Your API key is missing required permissions:")
			for perm in missing_perms:
				print(f"  - {perm}")
			print("Update the key permissions in Hydrus under 'services -> review services -> local -> client api'.")
			sys.exit(1)
	return can_edit_urls

def perform_rollback(api_url: str, api_key: str | None, rollback_path: str, custom_log_file: str | None):
	"""Reads a completed live migration log and reverts all applied URL additions/removals."""
	try:
		with open(rollback_path, "r", encoding="utf-8") as f:
			source_log = json.load(f)
	except (OSError, json.JSONDecodeError) as e:
		print(f"Error reading rollback log file '{rollback_path}': {e}")
		sys.exit(1)

	if source_log.get("dry_run", False):
		print("Error: The specified log file is from a DRY RUN. No changes were ever applied to Hydrus, so there is nothing to roll back.")
		sys.exit(1)

	if source_log.get("is_rollback", False):
		print("Error: The specified log file is already a rollback log.")
		sys.exit(1)

	applied_files = [entry for entry in source_log.get("files", []) if entry.get("action") == "applied"]
	if not applied_files:
		print("No applied file modifications found in the specified log file. Nothing to roll back.")
		sys.exit(0)

	while not api_key:
		api_key = input("Enter your Hydrus Client API Access Key: ").strip()

	headers = {"Hydrus-Client-API-Access-Key": api_key}
	verify_api_permissions(api_url, headers, require_search=False, require_edit=True)

	total_to_restore = sum(len(f.get("urls_removed", [])) for f in applied_files)
	total_to_remove = sum(len(f.get("urls_added", [])) for f in applied_files)

	print("\n============================================================")
	print("ROLLBACK PREVIEW")
	print(f"Source Log       : {rollback_path}")
	print(f"Original Run     : {source_log.get('timestamp', 'Unknown')}")
	print(f"Domain Migration : {source_log.get('old_domain')} -> {source_log.get('new_domain')} (Mode: {source_log.get('mode', '').upper()})")
	print(f"Files Affected   : {len(applied_files)}")
	print(f"URLs to Re-Add   : {total_to_restore} (originally removed)")
	print(f"URLs to Remove   : {total_to_remove} (originally added)")
	print("============================================================")

	try:
		confirmation = input("\nTo revert these exact changes in Hydrus now, type 'yes, rollback' (anything else will cancel): ").strip().lower()
	except (KeyboardInterrupt, EOFError):
		confirmation = ""

	if confirmation != "yes, rollback":
		print("\nRollback aborted. No changes were sent to Hydrus.")
		sys.exit(0)

	timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
	rollback_log_filename = custom_log_file or f"hydrus_url_ROLLBACK_{timestamp}.json"

	rollback_log_data = {
		"timestamp": datetime.now().isoformat(),
		"is_rollback": True,
		"rolled_back_from_log": rollback_path,
		"original_old_domain": source_log.get("old_domain"),
		"original_new_domain": source_log.get("new_domain"),
		"summary": {
			"files_reverted": 0,
			"total_urls_restored": 0,
			"total_urls_removed": 0,
			"errors": 0,
		},
		"files": [],
	}

	print("\n--- Executing Rollback ---")
	for entry in applied_files:
		file_hash = entry["hash"]
		urls_to_add = entry.get("urls_removed", [])
		urls_to_delete = entry.get("urls_added", [])

		rb_entry = {
			"hash": file_hash,
			"action": "reverted",
			"urls_restored": urls_to_add,
			"urls_removed": urls_to_delete,
		}

		payload = {
			"hash": file_hash,
			"urls_to_add": urls_to_add,
			"urls_to_delete": urls_to_delete,
		}

		try:
			post_res = requests.post(
				f"{api_url}/add_urls/associate_url",
				headers=headers,
				json=payload,
			)
			if not post_res.ok:
				raise requests.HTTPError(f"{post_res.status_code}: {post_res.text}")
		except requests.RequestException as e:
			rb_entry["action"] = "error"
			rb_entry["error"] = str(e)
			rollback_log_data["summary"]["errors"] += 1
			print(f"[ERROR] Failed reverting {file_hash}: {e}")

		rollback_log_data["files"].append(rb_entry)
		if rb_entry["action"] != "error":
			rollback_log_data["summary"]["files_reverted"] += 1
			rollback_log_data["summary"]["total_urls_restored"] += len(urls_to_add)
			rollback_log_data["summary"]["total_urls_removed"] += len(urls_to_delete)
			print(f"[REVERTED] {file_hash} | +{len(urls_to_add)} restored, -{len(urls_to_delete)} removed")

	with open(rollback_log_filename, "w", encoding="utf-8") as f:
		json.dump(rollback_log_data, f, indent=2)

	print("\n--- Rollback Summary ---")
	print(f"Files reverted        : {rollback_log_data['summary']['files_reverted']}")
	print(f"URLs restored         : {rollback_log_data['summary']['total_urls_restored']}")
	print(f"URLs removed          : {rollback_log_data['summary']['total_urls_removed']}")
	if rollback_log_data["summary"]["errors"]:
		print(f"Errors encountered    : {rollback_log_data['summary']['errors']}")
	print(f"Rollback log saved to : {rollback_log_filename}")

def prepare_hydrus_api_regex(pattern: str) -> tuple[str, list[str]]:
	"""
	Rewrites case-sensitive Python regex tokens into lowercase-safe equivalents for Hydrus's
	Client API search endpoint (workaround for https://github.com/hydrusnetwork/hydrus/issues/2122).
	Returns (api_safe_pattern, list_of_warnings).
	The original pattern is still used locally in Python for exact matching and substitution.
	"""
	warnings = []
	safe = pattern

	# 1. Named capture groups: (?P<name>...) -> (?:...)
	if re.search(r"\(\?P<[^>]+>", safe):
		warnings.append("Named capture group '(?P<name>...)' -> converted to '(?:...)' for API search")
		safe = re.sub(r"\(\?P<[^>]+>", "(?:", safe)

	# 2. Named backreferences: (?P=name) -> .* (broadened for API search; exact match enforced locally)
	if re.search(r"\(\?P=[^)]+\)", safe):
		warnings.append("Named backreference '(?P=name)' -> broadened to '.*' for API search (exact match enforced locally)")
		safe = re.sub(r"\(\?P=[^)]+\)", ".*", safe)

	# 3. Non-digit \D -> [^0-9] (prevents lowercasing to \d)
	if re.search(r"(?<!\\)(?:\\\\)*\\D", safe):
		warnings.append("Non-digit escape '\\D' -> converted to '[^0-9]' for API search")
		safe = re.sub(r"((?<!\\)(?:\\\\)*)\\D", r"\1[^0-9]", safe)

	# 4. Non-whitespace \S -> [^\s] (prevents lowercasing to \s)
	if re.search(r"(?<!\\)(?:\\\\)*\\S", safe):
		warnings.append("Non-whitespace escape '\\S' -> converted to '[^\\s]' for API search")
		safe = re.sub(r"((?<!\\)(?:\\\\)*)\\S", r"\1[^\\s]", safe)

	# 5. Non-word \W -> [^a-z0-9_] (prevents lowercasing to \w)
	if re.search(r"(?<!\\)(?:\\\\)*\\W", safe):
		warnings.append("Non-word escape '\\W' -> converted to '[^a-z0-9_]' for API search")
		safe = re.sub(r"((?<!\\)(?:\\\\)*)\\W", r"\1[^a-z0-9_]", safe)

	# 6. Start-of-string \A -> ^ (prevents lowercasing to \a ASCII bell)
	if re.search(r"(?<!\\)(?:\\\\)*\\A", safe):
		warnings.append("Start anchor '\\A' -> converted to '^' for API search")
		safe = re.sub(r"((?<!\\)(?:\\\\)*)\\A", r"\1^", safe)

	# 7. End-of-string \Z -> $ (prevents lowercasing to invalid escape \z)
	if re.search(r"(?<!\\)(?:\\\\)*\\Z", safe):
		warnings.append("End anchor '\\Z' -> converted to '$' for API search")
		safe = re.sub(r"((?<!\\)(?:\\\\)*)\\Z", r"\1$", safe)

	# 8. Non-word-boundary \B -> removed/broadened (prevents lowercasing to \b word boundary)
	if re.search(r"(?<!\\)(?:\\\\)*\\B", safe):
		warnings.append("Non-word-boundary '\\B' -> stripped for API search to avoid matching '\\b' (exact match enforced locally)")
		safe = re.sub(r"((?<!\\)(?:\\\\)*)\\B", r"\1", safe)

	# 9. Remaining uppercase ASCII letters (e.g., [A-Z] or literal uppercase URL paths)
	if re.search(r"[A-Z]", safe):
		warnings.append("Uppercase characters/ranges (e.g. A-Z) -> Hydrus API lowercases search strings (exact case enforced locally)")

	return safe, warnings



def main():
	args = parse_args()

	# Handle rollback mode separately before normal migration prompts
	if args.rollback:
		perform_rollback(args.api_url, args.api_key, args.rollback, args.log_file)
		return
	
	api_key, old_domain, new_domain, mode, dry_run, use_regex = get_interactive_inputs(args)

	compiled_regex = None
	if use_regex:
		try:
			compiled_regex = re.compile(old_domain)
		except re.error as e:
			print(f"Error: Invalid regular expression '{old_domain}': {e}")
			sys.exit(1)


	headers = {"Hydrus-Client-API-Access-Key": api_key}
	timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
	prefix = "DRYRUN_" if dry_run else ""
	log_filename = args.log_file or f"hydrus_url_migration_{prefix}{timestamp}.json"

	print("\n--- Configuration ---")
	print(f"API URL    : {args.api_url}")
	print(f"Match Type : {'REGEX' if use_regex else 'DOMAIN'}")
	print(f"Old Domain : {old_domain}")
	print(f"New Domain : {new_domain}")
	print(f"Mode       : {mode.upper()}")
	print(f"Dry Run    : {'YES (No changes will be made)' if dry_run else 'NO (Live execution)'}")
	print(f"Log File   : {log_filename}")
	print("---------------------\n")


	# 1. Verify API connection and check permissions
	can_edit_urls = verify_api_permissions(args.api_url, headers, require_search=True, require_edit=(not dry_run))


	# 2. Search for matching files
	if use_regex:
		hydrus_safe_regex, regex_warnings = prepare_hydrus_api_regex(old_domain)
		if regex_warnings:
			print("WARNING: Hydrus Client API lowercases regex search strings (see https://github.com/hydrusnetwork/hydrus/issues/2122).")
			print("Applying automatic workarounds for the API search query (your exact original regex will still be used locally):")
			for w in regex_warnings:
				print(f"  - {w}")
			print()
		print(f"Searching for files with known URLs matching regex '{hydrus_safe_regex}'...")
		predicate = f"system:has url matching regex {hydrus_safe_regex}"
	else:
		print(f"Searching for files with known URLs on domain '{old_domain}'...")
		predicate = f"system:has domain {old_domain}"

	search_params = {"tags": json.dumps([predicate])}
	search_res = requests.get(f"{args.api_url}/get_files/search_files", headers=headers, params=search_params)
	if not search_res.ok:
		print(f"API Error ({search_res.status_code}): {search_res.text}")
	search_res.raise_for_status()
	file_ids = search_res.json().get("file_ids", [])

	print(f"Found {len(file_ids)} candidate files.\n")

	log_data = {
		"timestamp": datetime.now().isoformat(),
		"dry_run": dry_run,
		"use_regex": use_regex,
		"old_domain": old_domain,
		"new_domain": new_domain,
		"mode": mode,
		"summary": {
			"candidate_files_found": len(file_ids),
			"files_modified": 0,
			"total_urls_added": 0,
			"total_urls_removed": 0,
			"errors": 0,
		},
		"files": [],
	}

	# 3. Process in batches
	for i in range(0, len(file_ids), args.batch_size):
		batch = file_ids[i : i + args.batch_size]
		meta_res = requests.get(
			f"{args.api_url}/get_files/file_metadata",
			headers=headers,
			params={"file_ids": json.dumps(batch)},
		)
		meta_res.raise_for_status()
		metadata_list = meta_res.json().get("metadata", [])

		for file_info in metadata_list:
			file_hash = file_info["hash"]
			known_urls = file_info.get("known_urls", [])

			urls_to_add = []
			urls_to_delete = []
			replacements_detail = []

			for url in known_urls:
				new_url = transform_url(url, old_domain, new_domain, use_regex, compiled_regex)
				if new_url and new_url != url:
					# Only queue addition if it isn't already on the file
					if new_url not in known_urls and new_url not in urls_to_add:
						urls_to_add.append(new_url)

					if mode == "replace":
						urls_to_delete.append(url)
						replacements_detail.append({"old_url": url, "new_url": new_url})

			if not urls_to_add and not urls_to_delete:
				continue

			file_entry = {
				"hash": file_hash,
				"action": "simulated" if dry_run else "applied",
				"urls_added": urls_to_add,
				"urls_removed": urls_to_delete,
			}
			if mode == "replace":
				file_entry["replaced_pairs"] = replacements_detail

			if not dry_run:
				payload = {
					"hash": file_hash,
					"urls_to_add": urls_to_add,
					"urls_to_delete": urls_to_delete,
				}
				try:
					post_res = requests.post(
						f"{args.api_url}/add_urls/associate_url",
						headers=headers,
						json=payload,
					)
					post_res.raise_for_status()
				except requests.RequestException as e:
					file_entry["action"] = "error"
					file_entry["error"] = str(e)
					log_data["summary"]["errors"] += 1
					print(f"[ERROR] Failed updating {file_hash}: {e}")

			log_data["files"].append(file_entry)
			if file_entry["action"] != "error":
				log_data["summary"]["files_modified"] += 1
				log_data["summary"]["total_urls_added"] += len(urls_to_add)
				log_data["summary"]["total_urls_removed"] += len(urls_to_delete)

				tag = "[DRY RUN]" if dry_run else "[UPDATED]"
				print(f"{tag} {file_hash} | +{len(urls_to_add)} added, -{len(urls_to_delete)} removed")


	# 4. Calculate Dry Run Averages & Outliers
	modified_count = log_data["summary"]["files_modified"]
	if dry_run and modified_count > 0:
		avg_added = log_data["summary"]["total_urls_added"] / modified_count
		rounded_added = round_half_up(avg_added)

		avg_removed = log_data["summary"]["total_urls_removed"] / modified_count
		rounded_removed = round_half_up(avg_removed)

		outliers = []
		for entry in log_data["files"]:
			added_cnt = len(entry["urls_added"])
			removed_cnt = len(entry["urls_removed"])

			diff_added = added_cnt != rounded_added
			diff_removed = (mode == "replace") and (removed_cnt != rounded_removed)

			if diff_added or diff_removed:
				outliers.append({
					"hash": entry["hash"],
					"urls_added_count": added_cnt,
					"urls_removed_count": removed_cnt,
					"urls_added": entry["urls_added"],
					"urls_removed": entry["urls_removed"],
				})

		log_data["dry_run_analysis"] = {
			"average_urls_added_per_file": avg_added,
			"rounded_average_urls_added": rounded_added,
			"average_urls_removed_per_file": avg_removed if mode == "replace" else 0,
			"rounded_average_urls_removed": rounded_removed if mode == "replace" else 0,
			"outlier_files_count": len(outliers),
			"outlier_files": outliers,
		}

	# 5. Write output log
	with open(log_filename, "w", encoding="utf-8") as f:
		json.dump(log_data, f, indent=2)

	print("\n--- Summary ---")
	print(f"Files {'that would be ' if dry_run else ''}modified : {modified_count}")
	print(f"URLs {'that would be ' if dry_run else ''}added    : {log_data['summary']['total_urls_added']}")
	print(f"URLs {'that would be ' if dry_run else ''}removed  : {log_data['summary']['total_urls_removed']}")
	if log_data["summary"]["errors"]:
		print(f"Errors encountered    : {log_data['summary']['errors']}")

	if dry_run and modified_count > 0:
		analysis = log_data["dry_run_analysis"]
		print("\n--- Dry Run Anomaly Check ---")
		print(f"Avg URLs added/file   : {analysis['average_urls_added_per_file']:.5f} (expected whole number: {analysis['rounded_average_urls_added']})")
		if mode == "replace":
			print(f"Avg URLs removed/file : {analysis['average_urls_removed_per_file']:.5f} (expected whole number: {analysis['rounded_average_urls_removed']})")

		outliers = analysis["outlier_files"]
		if outliers:
			print(f"\nFiles differing from the rounded average ({len(outliers)} found):")
			for item in outliers:
				if mode == "replace":
					print(f"\n  - {item['hash']} (+{item['urls_added_count']} added, -{item['urls_removed_count']} removed)")
				else:
					print(f"\n  - {item['hash']} (+{item['urls_added_count']} added)")

				for url in item["urls_added"]:
					print(f"      [+] {url}")
				for url in item["urls_removed"]:
					print(f"      [-] {url}")
		else:
			print("\nAll files match the rounded average! No outliers found.")

	print(f"\nFull log saved to     : {log_filename}")

	# 6. Explicit confirmation prompt to execute live run after a dry run
	if dry_run and modified_count > 0:
		print("\n============================================================")
		print("DRY RUN COMPLETE — NO CHANGES HAVE BEEN MADE TO HYDRUS YET.")
		if not can_edit_urls:
			print("\nNote: Your API key currently lacks 'Import and Edit URLs' (ID 0) permission.")
			print("Grant that permission in Hydrus before performing a live run.")
			print("============================================================")
			sys.exit(0)
		print(f"Ready to {mode.upper()} URLs on {modified_count} file(s).")
		print("Make sure you have backed up your Hydrus database before proceeding.")
		print("============================================================")



		try:
			confirmation = input("\nTo apply these exact changes to Hydrus now, type 'yes, run' (anything else will cancel): ").strip().lower()
		except (KeyboardInterrupt, EOFError):
			confirmation = ""

		if confirmation == "yes, run":
			live_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
			live_log_filename = f"hydrus_url_migration_{live_timestamp}.json"
			execute_live_changes(
				api_url=args.api_url,
				headers=headers,
				planned_files=log_data["files"],
				old_domain=old_domain,
				new_domain=new_domain,
				mode=mode,
				candidate_count=len(file_ids),
				log_filename=live_log_filename,
			)
		else:
			print("\nAborted. No changes were sent to Hydrus.")





if __name__ == "__main__":
	main()
