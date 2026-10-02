#!/usr/bin/env python3
"""Local feedback workspace: saved runs, sequential batches, and exports."""

import argparse
import csv
import hashlib
import hmac
import io
import json
import os
import re
import secrets
import threading
import urllib.error
import uuid
import webbrowser
from datetime import date, datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

from baseline import predict
from insight import INSTRUCTIONS, parse_insight
from zero_shot import call_model

HERE = Path(__file__).parent
DATA = HERE / "local_data"
MAX_BODY = 4 * 1024 * 1024
MAX_REVIEW = 2000
MAX_ROWS = 500
csv.field_size_limit(MAX_BODY)
PROMPT_HASH = hashlib.sha256(INSTRUCTIONS.encode()).hexdigest()
ENGLISH = json.loads((HERE / "ui_en.json").read_text(encoding="utf-8"))


def english_message(text):
    if text in ENGLISH:
        return ENGLISH[text]
    match = re.fullmatch(r"第 (\d+) 条评论需要 1–2000 个字符。", text)
    if match:
        return f"Review {match[1]} must contain 1 to 2000 characters."
    match = re.fullmatch(r"CSV 第 (\d+) 行格式不完整，或评论为空/超过 2000 字符。", text)
    if match:
        return f"CSV row {match[1]} is incomplete, empty or exceeds 2000 characters."
    match = re.fullmatch(r"无法读取历史文件 (.+)；原文件保留。", text)
    if match:
        return f"Cannot read history file {match[1]}. The original file was preserved."
    return text


def english_response(value, field=""):
    # Translate interface diagnostics only; never translate user reviews or model evidence.
    if isinstance(value, dict):
        return {key: english_response(item, key) for key, item in value.items()}
    if isinstance(value, list):
        return [english_response(item, field) for item in value]
    if isinstance(value, str) and field in {"error", "errors", "warnings", "title"}:
        return english_message(value)
    return value


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def validate_reviews(value):
    if not isinstance(value, list) or not 1 <= len(value) <= MAX_ROWS:
        raise ValueError("一次需要 1–500 条评论。")
    result = []
    for number, row in enumerate(value, 1):
        text = row.get("review") if isinstance(row, dict) else None
        if not isinstance(text, str) or not text.strip() or len(text) > MAX_REVIEW:
            raise ValueError(f"第 {number} 条评论需要 1–2000 个字符。")
        source_id = str(row.get("review_id", number))[:100]
        result.append({"review_id": source_id, "review": text.strip(),
                       "baseline_category": predict(text.strip()), "status": "pending",
                       "result": None, "error": "", "attempts": []})
    return result


def parse_csv(text):
    if not isinstance(text, str) or len(text.encode("utf-8")) > 2 * 1024 * 1024:
        raise ValueError("CSV 文件不能超过 2 MB。")
    reader = csv.DictReader(io.StringIO(text.lstrip("\ufeff")))
    if not reader.fieldnames or "review" not in reader.fieldnames:
        raise ValueError("CSV 第一行必须有 review 列；可另有 review_id 列。")
    if len(reader.fieldnames) != len(set(reader.fieldnames)):
        raise ValueError("CSV 列名不能重复。")
    rows, errors = [], []
    for number, row in enumerate(reader, 2):
        if number > MAX_ROWS + 1:
            raise ValueError("每个 CSV 最多 500 条数据，请拆分文件。")
        text = row.get("review")
        if None in row or not isinstance(text, str) or not text.strip() or len(text) > MAX_REVIEW:
            errors.append(f"CSV 第 {number} 行格式不完整，或评论为空/超过 2000 字符。")
        else:
            rows.append({"review_id": row.get("review_id") or str(number - 1), "review": text.strip()})
    if not rows:
        raise ValueError("没有可分析的评论。")
    return {"reviews": rows, "errors": errors, "count": len(rows)}


def summary(job):
    statuses = [row["status"] for row in job["rows"]]
    return {key: job[key] for key in ("id", "title", "method", "created_at", "updated_at", "status")} | {
        "total": len(statuses), "done": sum(s in {"success", "failed", "invalid", "interrupted"} for s in statuses),
        "success": statuses.count("success"),
        "failed": sum(s in {"failed", "invalid", "interrupted"} for s in statuses),
        "pending": statuses.count("pending"),
    }


class Workspace:
    def __init__(self, directory, provider, model):
        self.directory = directory
        directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.provider = provider
        self.model = model
        self.jobs = {}
        self.warnings = []
        self.active = None
        # ponytail: one local worker; parallel processing can be added if throughput matters.
        self.lock = threading.RLock()
        for path in directory.glob("*.json"):
            try:
                job = json.loads(path.read_text(encoding="utf-8"))
                if not re.fullmatch(r"[a-f0-9]{32}", path.stem) or path.stem != job["id"] or not isinstance(job["rows"], list):
                    raise ValueError("invalid run file")
                self.jobs[job["id"]] = job
                if job["status"] in {"running", "pausing"}:
                    job["status"] = "paused"
                    for row in job["rows"]:
                        if row["status"] == "processing":
                            row["status"] = "interrupted"
                            row["error"] = "服务中断，无法确定请求是否已完成或计费；不会自动重发。"
                    self.save(job)
            except (ValueError, KeyError, TypeError):
                self.warnings.append(f"无法读取历史文件 {path.name}；原文件保留。")

    def save(self, job):
        job["updated_at"] = now()
        target = self.directory / (job["id"] + ".json")
        temporary = target.with_suffix(".tmp")
        descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(descriptor, "w", encoding="utf-8") as f:
            json.dump(job, f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())
        temporary.replace(target)

    def key(self):
        value = os.environ.get("OPENROUTER_API_KEY" if self.provider == "openrouter" else "OPENAI_API_KEY")
        if not value and self.provider == "openrouter":
            path = DATA / ".openrouter_key"
            if path.exists():
                value = path.read_text(encoding="utf-8").strip()
        return value

    def get(self, job_id):
        with self.lock:
            if job_id not in self.jobs:
                raise KeyError("未找到这次分析。")
            return json.loads(json.dumps(self.jobs[job_id]))

    def create(self, data):
        method = data.get("method")
        if method not in {"ai", "rule"}:
            raise ValueError("分析方式必须为 ai 或 rule。")
        rows = validate_reviews(data.get("reviews"))
        with self.lock:
            if method == "ai" and not self.key():
                raise ValueError("尚未配置 API 密钥。请通过启动入口设置后重新打开。")
            if method == "ai" and self.active:
                raise ValueError("已有 AI 分析运行中，请先等待或暂停它。")
            job = {"id": uuid.uuid4().hex, "title": str(data.get("title") or "评论分析")[:100],
                   "method": method, "created_at": now(), "updated_at": now(),
                   "status": "paused", "provider": self.provider, "model": self.model,
                   "prompt_sha256": PROMPT_HASH, "rows": rows}
            self.jobs[job["id"]] = job
            if method == "rule":
                for row in rows:
                    row["status"] = "success"
                job["status"] = "completed"
            self.save(job)
            if method == "ai":
                self.start(job)
            return self.get(job["id"])

    def report_period(self, job_id, data):
        app = data.get("app_name")
        if not isinstance(app, str) or not app.strip() or len(app) > 100:
            raise ValueError("请填写应用名称（1–100字符）。")
        try:
            day = date.fromisoformat(data.get("report_week", ""))
        except (TypeError, ValueError):
            raise ValueError("请选择评论所属周的日期。")
        with self.lock:
            job = self.jobs.get(job_id)
            if not job:
                raise KeyError()
            job["app_name"] = app.strip()
            job["report_week"] = (day - timedelta(days=day.weekday())).isoformat()
            self.save(job)
            return self.get(job_id)

    def start(self, job):
        if self.active:
            raise ValueError("已有 AI 分析运行中，请等待当前请求完成。")
        if job["prompt_sha256"] != PROMPT_HASH or (job["provider"], job["model"]) != (self.provider, self.model):
            raise ValueError("这次历史分析使用了不同提示词或模型；请新建分析，避免混合结果。")
        if not self.key():
            raise ValueError("尚未配置 API 密钥，请重新通过启动入口设置。")
        if not any(row["status"] == "pending" for row in job["rows"]):
            raise ValueError("没有待处理项。失败项需单独点击重试。")
        job["status"] = "running"
        self.save(job)
        self.active = job["id"]
        threading.Thread(target=self.run, args=(job["id"],), daemon=True).start()

    def action(self, job_id, action):
        with self.lock:
            job = self.jobs.get(job_id)
            if not job:
                raise KeyError("未找到这次分析。")
            if job["method"] != "ai":
                raise ValueError("关键词分析已完成，无需暂停或继续。")
            if action == "pause":
                if job["status"] == "running":
                    job["status"] = "pausing"
                    self.save(job)
            elif action in {"resume", "retry"}:
                if self.active:
                    raise ValueError("请先等待当前请求完成。")
                # Validate before changing saved rows, including on retry.
                if not self.key() or job["prompt_sha256"] != PROMPT_HASH or (job["provider"], job["model"]) != (self.provider, self.model):
                    raise ValueError("密钥未配置或模型/提示词已变更；请配置密钥或新建分析。")
                if action == "retry":
                    for row in job["rows"]:
                        if row["status"] in {"failed", "invalid", "interrupted"}:
                            row["status"] = "pending"
                            row["error"] = ""
                self.start(job)
            else:
                raise ValueError("未知操作。")
            return self.get(job_id)

    def run(self, job_id):
        job = self.jobs[job_id]
        try:
            for row in job["rows"]:
                with self.lock:
                    if job["status"] != "running":
                        break
                    if row["status"] != "pending":
                        continue
                    row["status"] = "processing"
                    self.save(job)
                attempt = {"started_at": now(), "raw_output": "", "input_tokens": 0, "output_tokens": 0}
                stop = False
                try:
                    raw, latency, usage = call_model(row["review"], self.key(), job["model"], job["provider"], INSTRUCTIONS)
                    value = parse_insight(raw, row["review"])
                    attempt.update(raw_output=raw, latency_ms=latency,
                                   input_tokens=usage.get("input_tokens") or 0,
                                   output_tokens=usage.get("output_tokens") or 0)
                    status = "success" if value else "invalid"
                    error = "" if value else "模型字段不符合要求，或引用未逐字匹配原评论。原始响应已保存。"
                except (urllib.error.URLError, TimeoutError, KeyError, TypeError, ValueError):
                    value, status = None, "failed"
                    error = "API 请求失败，已暂停。请检查网络、密钥或余额；失败请求是否计费以服务商记录为准。"
                    stop = True
                with self.lock:
                    attempt.update(status=status, error=error, finished_at=now())
                    row["attempts"].append(attempt)
                    row.update(status=status, result=value, error=error)
                    if stop:
                        job["status"] = "paused"
                    self.save(job)
                if stop:
                    break
        except Exception:
            # Preserve existing progress if local persistence or an unexpected worker error fails.
            with self.lock:
                for row in job["rows"]:
                    if row["status"] == "processing":
                        row["status"] = "interrupted"
                        row["error"] = "处理意外中断，不会自动重发；请检查存储空间并手动确认是否重试。"
                job["status"] = "paused"
        finally:
            with self.lock:
                job["status"] = "paused" if any(r["status"] == "pending" for r in job["rows"]) else "completed"
                try:
                    self.save(job)
                finally:
                    self.active = None


def csv_export(job):
    fields = ["review_id", "review", "baseline_category", "status", "category", "issue_topic",
              "severity", "user_need", "evidence", "error", "input_tokens", "output_tokens"]
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fields)
    writer.writeheader()
    for row in job["rows"]:
        record = {key: row.get(key, "") for key in fields}
        record.update(row.get("result") or {})
        record["input_tokens"] = sum(a.get("input_tokens", 0) for a in row["attempts"])
        record["output_tokens"] = sum(a.get("output_tokens", 0) for a in row["attempts"])
        # CSV opened in spreadsheet apps must not execute user-supplied formula text.
        for key, value in record.items():
            if isinstance(value, str) and value.lstrip().startswith(("=", "+", "-", "@")):
                record[key] = "'" + value
        writer.writerow(record)
    return ("\ufeff" + output.getvalue()).encode("utf-8")


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_args):
        pass

    def send(self, status, body, content_type="application/json; charset=utf-8", filename=None):
        if not isinstance(body, bytes):
            if self.headers.get("X-App-Language", "") == "en":
                body = english_response(body)
            body = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        if filename:
            self.send_header("Content-Disposition", f'attachment; filename="{filename}"')
        self.end_headers()
        self.wfile.write(body)

    def authorized(self):
        host = self.headers.get("Host", "").split(":")[0]
        if self.server.local_only and host not in {"127.0.0.1", "localhost", "["}:
            self.send(403, {"error": "请通过本机地址打开网页。"})
            return False
        if not hmac.compare_digest(self.headers.get("X-App-Token", ""), self.server.token):
            self.send(403, {"error": "请刷新网页后重试。"})
            return False
        if self.server.access_code and not hmac.compare_digest(self.headers.get("X-Access-Code", ""), self.server.access_code):
            self.send(403, {"error": "需要访问码。", "access_code_required": True})
            return False
        return True

    def do_GET(self):
        path = urlsplit(self.path).path
        if path in {"/", "/index.html", "/en", "/index_en.html", "/zh"}:
            english = path in {"/en", "/index_en.html"} or (path in {"/", "/index.html"} and self.server.language == "en")
            filename = "index_en.html" if english else "index.html"
            body = (HERE / filename).read_text().replace("__APP_TOKEN__", self.server.token)
            self.send(200, body.encode(), "text/html; charset=utf-8")
            return
        if not path.startswith("/api/") or not self.authorized():
            if not path.startswith("/api/"):
                self.send(404, {"error": "未找到页面。"})
            return
        workspace = self.server.workspace
        try:
            if path == "/api/status":
                self.send(200, {"ai_ready": bool(workspace.key()), "model": workspace.model,
                                "max_rows": MAX_ROWS, "warnings": workspace.warnings})
            elif path == "/api/jobs":
                with workspace.lock:
                    jobs = sorted((summary(j) for j in workspace.jobs.values()), key=lambda j: j["created_at"], reverse=True)
                self.send(200, {"jobs": jobs})
            else:
                match = re.fullmatch(r"/api/jobs/([a-f0-9]{32})(?:/(csv|json))?", path)
                if not match:
                    raise KeyError()
                job = workspace.get(match[1])
                if self.headers.get("X-App-Language", "") == "en":
                    job = english_response(job)
                if match[2] == "csv":
                    self.send(200, csv_export(job), "text/csv; charset=utf-8", f"feedback-{match[1][:8]}.csv")
                elif match[2] == "json":
                    self.send(200, json.dumps(job, ensure_ascii=False, indent=2).encode(), filename=f"feedback-{match[1][:8]}.json")
                else:
                    self.send(200, job)
        except KeyError:
            self.send(404, {"error": "未找到分析记录。"})

    def do_POST(self):
        if not self.authorized():
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 < length <= MAX_BODY:
                raise ValueError("请求为空或过大，CSV 最多 2 MB。")
            data = json.loads(self.rfile.read(length))
            if not isinstance(data, dict):
                raise ValueError("请求格式错误。")
            workspace = self.server.workspace
            path = urlsplit(self.path).path
            if path == "/api/import":
                result = parse_csv(data.get("csv"))
            elif path == "/api/jobs":
                result = workspace.create(data)
            elif re.fullmatch(r"/api/jobs/[a-f0-9]{32}/report-period", path):
                result = workspace.report_period(path.split("/")[3], data)
            else:
                match = re.fullmatch(r"/api/jobs/([a-f0-9]{32})/(pause|resume|retry)", path)
                if not match:
                    raise KeyError()
                result = workspace.action(match[1], match[2])
            self.send(200, result)
        except (ValueError, UnicodeDecodeError) as error:
            self.send(400, {"error": str(error)})
        except csv.Error:
            self.send(400, {"error": "CSV 格式无法读取，请检查引号、分隔符和编码。"})
        except KeyError:
            self.send(404, {"error": "未找到分析记录或操作。"})
        except OSError:
            self.send(500, {"error": "无法保存本地记录，请检查磁盘空间和文件权限。"})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--provider", choices=("auto", "openai", "openrouter"), default="auto")
    parser.add_argument("--model")
    parser.add_argument("--language", choices=("zh", "en"), default="en")
    parser.add_argument("--open", action="store_true", help="Open the default browser")
    args = parser.parse_args()
    saved_key = DATA / ".openrouter_key"
    if not os.environ.get("OPENROUTER_API_KEY") and saved_key.exists():
        os.environ["OPENROUTER_API_KEY"] = saved_key.read_text().strip()
    provider = args.provider
    if provider == "auto":
        provider = "openrouter" if os.environ.get("OPENROUTER_API_KEY") else "openai"
    model = args.model or ("openai/gpt-4o-mini" if provider == "openrouter" else "gpt-6-luna")
    # One process owns the history folder, avoiding competing workers after double-clicking twice.
    import fcntl
    DATA.mkdir(exist_ok=True, mode=0o700)
    lock_file = (DATA / ".server.lock").open("a")
    try:
        fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        print("The app is already running. Opening its page." if args.language == "en" else "本地应用已经运行，正在打开已运行的网页。")
        address_file = DATA / ".server_url"
        if args.open and address_file.exists():
            address = address_file.read_text().strip()
            if re.fullmatch(r"http://127\.0\.0\.1:[0-9]+", address):
                webbrowser.open(address + ("/en" if args.language == "en" else "/zh"))
        return
    try:
        server = ThreadingHTTPServer((args.host, args.port), Handler)
    except OSError as error:
        raise SystemExit(f"Could not start: {error}. Close the program using this port or select another port with --port." if args.language == "en" else f"无法启动：{error}。请关闭占用端口的程序或通过 --port 换端口。")
    server.workspace = Workspace(DATA / "runs", provider, model)
    server.language = args.language
    server.token = secrets.token_urlsafe(24)
    server.local_only = args.host in {"127.0.0.1", "localhost", "::1"}
    server.access_code = None if server.local_only else secrets.token_urlsafe(12)
    address = f"http://127.0.0.1:{server.server_address[1]}"
    (DATA / ".server_url").write_text(address)
    message = (f"Open {address}/en\nHistory: {DATA / 'runs'}\nKeep this window open; Ctrl+C stops the service." if args.language == "en" else f"打开 {address}/zh\n历史记录保存到 {DATA / 'runs'}\n保持此窗口打开；按 Ctrl+C 停止。")
    print(message, flush=True)
    if server.access_code:
        print(f"LAN access code: {server.access_code}" if args.language == "en" else f"局域网访问码：{server.access_code}", flush=True)
    if args.open:
        webbrowser.open(address + ("/en" if args.language == "en" else "/zh"))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nService stopped. Unsaved requests will be marked interrupted on restart and will not be automatically resent." if args.language == "en" else "\n服务已停止。进行中的请求可能尚未保存；重启后会标记为中断，不会自动重发。")
    finally:
        server.server_close()
        lock_file.close()


if __name__ == "__main__":
    main()
