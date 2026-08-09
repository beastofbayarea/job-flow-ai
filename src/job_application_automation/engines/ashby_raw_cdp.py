"""Strict, fill-only Ashby automation over a target-level CDP websocket.

This helper intentionally has no submission support and does not use Playwright.
"""

from __future__ import annotations

import argparse
import json
import time
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from websockets.sync.client import connect


@dataclass(frozen=True)
class FillResult:
    success: bool
    status: str
    target_id: str
    url: str
    title: str
    filled: dict[str, str]
    attached_files: list[str]
    visible_files: list[str]
    required_empty: list[str]
    errors: list[str]
    submitted: bool = False


class CdpTarget:
    def __init__(self, websocket_url: str, timeout_seconds: float) -> None:
        self._timeout = timeout_seconds
        self._next_id = 0
        self._websocket = connect(
            websocket_url,
            open_timeout=timeout_seconds,
            close_timeout=1,
        )

    def close(self) -> None:
        self._websocket.close()

    def call(self, method: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        self._next_id += 1
        request_id = self._next_id
        self._websocket.send(
            json.dumps({"id": request_id, "method": method, "params": params or {}})
        )
        deadline = time.monotonic() + self._timeout
        while time.monotonic() < deadline:
            message = json.loads(
                self._websocket.recv(timeout=max(0.1, deadline - time.monotonic()))
            )
            if message.get("id") != request_id:
                continue
            if "error" in message:
                raise RuntimeError(f"CDP {method} failed: {message['error']}")
            return message.get("result", {})
        raise TimeoutError(f"CDP {method} exceeded {self._timeout:.1f}s")


def _json_url(endpoint: str, path: str, timeout: float) -> Any:
    with urllib.request.urlopen(endpoint.rstrip("/") + path, timeout=timeout) as response:
        return json.load(response)


def _target(endpoint: str, target_id: str, timeout: float) -> dict[str, Any]:
    targets = _json_url(endpoint, "/json/list", timeout)
    target = next((item for item in targets if item.get("id") == target_id), None)
    if not target or not target.get("webSocketDebuggerUrl"):
        raise RuntimeError(f"Exact Chrome target is unavailable: {target_id}")
    return target


def _application_url(url: str) -> str:
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme != "https" or parsed.netloc.casefold() != "jobs.ashbyhq.com":
        raise ValueError("URL must be an HTTPS jobs.ashbyhq.com URL")
    path = parsed.path.rstrip("/")
    if not path.endswith("/application"):
        path += "/application"
    return urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, path, "", ""))


def _evaluate(cdp: CdpTarget, expression: str) -> Any:
    result = cdp.call(
        "Runtime.evaluate",
        {"expression": expression, "returnByValue": True, "awaitPromise": True},
    )
    exception = result.get("exceptionDetails")
    if exception:
        raise RuntimeError(f"Runtime.evaluate failed: {exception}")
    return result.get("result", {}).get("value")


def _wait_for_form(cdp: CdpTarget, render_timeout: float) -> None:
    deadline = time.monotonic() + render_timeout
    while time.monotonic() < deadline:
        ready = _evaluate(
            cdp,
            "Boolean(document.querySelector('.ashby-application-form-field-entry, input[type=file]'))",
        )
        if ready:
            return
        time.sleep(0.25)
    raise TimeoutError(f"Ashby form did not render within {render_timeout:.1f}s")


def fill_ashby_target(
    *,
    endpoint: str,
    target_id: str,
    url: str,
    resume: Path,
    values: dict[str, str],
    answers: dict[str, str],
    command_timeout: float = 6.0,
    render_timeout: float = 10.0,
    navigate: bool = True,
) -> FillResult:
    resume = resume.resolve(strict=True)
    application_url = _application_url(url)
    errors: list[str] = []
    cdp: CdpTarget | None = None
    try:
        target = _target(endpoint, target_id, command_timeout)
        cdp = CdpTarget(target["webSocketDebuggerUrl"], command_timeout)
        cdp.call("Runtime.enable")
        cdp.call("Page.enable")
        cdp.call("DOM.enable")
        if navigate:
            cdp.call("Page.navigate", {"url": application_url})
        _wait_for_form(cdp, render_timeout)

        payload = json.dumps({"values": values, "answers": answers})
        fill_script = r"""
        ((payload) => {
          const normalize = value => (value || '').replace(/\s+/g, ' ').trim().toLowerCase();
          const setValue = (element, value) => {
            const descriptor = Object.getOwnPropertyDescriptor(
              Object.getPrototypeOf(element), 'value'
            );
            if (descriptor && descriptor.set) descriptor.set.call(element, value);
            else element.value = value;
            element.dispatchEvent(new Event('input', {bubbles: true}));
            element.dispatchEvent(new Event('change', {bubbles: true}));
          };
          const exact = new Map(Object.entries(payload.answers).map(([k, v]) => [normalize(k), v]));
          const systemFields = new Map([
            ['_systemfield_name', payload.values.name],
            ['_systemfield_email', payload.values.email],
            ['_systemfield_phone', payload.values.phone],
            ['_systemfield_location', payload.values.location],
            ['_systemfield_linkedin', payload.values.linkedin]
          ]);
          const aliases = [
            [['name', 'full name'], payload.values.name],
            [['first name'], payload.values.first_name],
            [['last name'], payload.values.last_name],
            [['email', 'email address'], payload.values.email],
            [['phone', 'phone number'], payload.values.phone],
            [['location', 'current location', 'city', 'country'], payload.values.location],
            [['linkedin', 'linkedin profile', 'link to your linkedin profile'], payload.values.linkedin],
            [['twitter', 'twitter handle', 'x profile', 'x handle'], payload.values.twitter]
          ];
          const filled = {};
          for (const container of document.querySelectorAll(
            '.ashby-application-form-field-entry, fieldset, [role="group"]'
          )) {
            const heading = container.querySelector(
              '.ashby-application-form-question-title, label, legend'
            );
            const label = (heading?.textContent || container.innerText?.split('\n')[0] || '').trim();
            const key = normalize(label);
            const control = container.querySelector(
              'input:not([type=file]):not([type=hidden]):not([type=radio]):not([type=checkbox]), textarea'
            );
            if (!control || control.disabled || control.readOnly) continue;
            const systemToken = [...systemFields.keys()].find(token =>
              (control.name || '').toLowerCase().includes(token)
            );
            let value = (systemToken && systemFields.get(systemToken)) || exact.get(key) || '';
            if (!value) {
              for (const [names, candidate] of aliases) {
                if (candidate && names.some(name => key === name || key.startsWith(name + ' '))) {
                  value = candidate;
                  break;
                }
              }
            }
            if (!value) continue;
            setValue(control, value);
            filled[label] = control.value;
          }
          for (const container of document.querySelectorAll(
            '.ashby-application-form-field-entry, fieldset, [role="group"]'
          )) {
            const heading = container.querySelector(
              '.ashby-application-form-question-title, label, legend'
            );
            const label = (heading?.textContent || container.innerText?.split('\n')[0] || '').trim();
            const answer = exact.get(normalize(label));
            if (!answer) continue;
            const wanted = normalize(answer);
            const options = [...container.querySelectorAll(
              'label, button, [role="option"], [role="radio"], [role="checkbox"]'
            )];
            const option = options.find(element => normalize(element.textContent) === wanted);
            if (option) {
              option.click();
              filled[label] = answer;
              continue;
            }
            const combobox = container.querySelector('[role="combobox"]');
            if (combobox) {
              combobox.click();
              const scopedOption = [...container.querySelectorAll('[role="option"]')]
                .find(element => normalize(element.textContent) === wanted);
              if (scopedOption) {
                scopedOption.click();
                filled[label] = answer;
              }
            }
          }
          return filled;
        })
        """ + f"({payload})"
        filled = _evaluate(cdp, fill_script) or {}

        document = cdp.call("DOM.getDocument", {"depth": -1, "pierce": True})
        root_id = document["root"]["nodeId"]
        selected_file_input = _evaluate(
            cdp,
            r"""
            (() => {
              for (const element of document.querySelectorAll('input[type=file]')) {
                element.removeAttribute('data-ashby-raw-resume-target');
              }
              const normalize = value => (value || '').replace(/\s+/g, ' ').trim().toLowerCase();
              const candidates = [...document.querySelectorAll('input[type=file]')].filter(element => {
                if (element.disabled) return false;
                const container = element.closest(
                  '.ashby-application-form-field-entry, fieldset, [role="group"]'
                );
                const heading = container?.querySelector(
                  '.ashby-application-form-question-title, label, legend'
                );
                const label = normalize(heading?.textContent || container?.innerText?.split('\n')[0]);
                return label === 'resume' || label.startsWith('resume ') || label.includes('resume')
                  || label === 'cv' || label.startsWith('cv ') || label.includes('resume/cv');
              });
              if (!candidates.length) return false;
              candidates[0].setAttribute('data-ashby-raw-resume-target', 'true');
              return true;
            })()
            """,
        )
        if not selected_file_input:
            raise RuntimeError("Enabled Resume-labeled Ashby file input was not found")
        file_node = cdp.call(
            "DOM.querySelector",
            {
                "nodeId": root_id,
                "selector": "input[type=file][data-ashby-raw-resume-target=true]",
            },
        ).get("nodeId", 0)
        if not file_node:
            raise RuntimeError("Ashby resume file input was not found")
        cdp.call("DOM.setFileInputFiles", {"nodeId": file_node, "files": [str(resume)]})
        time.sleep(0.5)

        verification = _evaluate(
            cdp,
            r"""
            (() => {
              const normalize = value => (value || '').replace(/\s+/g, ' ').trim();
              const rows = {};
              for (const container of document.querySelectorAll(
                '.ashby-application-form-field-entry, fieldset, [role="group"]'
              )) {
                const heading = container.querySelector(
                  '.ashby-application-form-question-title, label, legend'
                );
                const label = normalize(heading?.textContent || container.innerText?.split('\n')[0]);
                const control = container.querySelector('input, textarea, select');
                if (label && control && control.type !== 'password') rows[label] = control.value || '';
              }
              const resumeInputs = [...document.querySelectorAll(
                'input[type=file][data-ashby-raw-resume-target=true]'
              )].filter(element => !element.disabled);
              const files = resumeInputs
                .flatMap(element => [...(element.files || [])].map(file => file.name));
              const visibleFiles = resumeInputs
                .filter(element => element.offsetParent !== null)
                .flatMap(element => [...(element.files || [])].map(file => file.name));
              const requiredEmpty = [...document.querySelectorAll('input[required], textarea[required], select[required]')]
                .filter(element => {
                  if (element.disabled || element.offsetParent === null) return false;
                  if (element.type === 'file') return !(element.files && element.files.length);
                  if (element.type === 'radio' || element.type === 'checkbox') return false;
                  return !element.value;
                })
                .map(element => normalize(
                  element.closest('.ashby-application-form-field-entry, fieldset, [role="group"]')
                    ?.querySelector('.ashby-application-form-question-title, label, legend')?.textContent
                    || element.name
                ));
              return {url: location.href, title: document.title, rows, files, visibleFiles, requiredEmpty};
            })()
            """,
        )
        exact_url = verification.get("url") == application_url
        attached = verification.get("files", [])
        required_empty = verification.get("requiredEmpty", [])
        success = exact_url and resume.name in attached and not required_empty
        return FillResult(
            success=success,
            status="FILLED" if success else "PARTIALLY_FILLED",
            target_id=target_id,
            url=verification.get("url", application_url),
            title=verification.get("title", ""),
            filled=verification.get("rows", filled),
            attached_files=attached,
            visible_files=verification.get("visibleFiles", []),
            required_empty=required_empty,
            errors=errors,
        )
    except Exception as exc:  # CLI boundary: always emit a machine-readable result.
        errors.append(f"{type(exc).__name__}: {exc}")
        return FillResult(
            success=False,
            status="FAILED",
            target_id=target_id,
            url=application_url,
            title="",
            filled={},
            attached_files=[],
            visible_files=[],
            required_empty=[],
            errors=errors,
        )
    finally:
        if cdp is not None:
            cdp.close()


def _mapping(value: str) -> dict[str, str]:
    parsed = json.loads(value)
    if not isinstance(parsed, dict) or not all(
        isinstance(key, str) and isinstance(item, str) for key, item in parsed.items()
    ):
        raise argparse.ArgumentTypeError("value must be a JSON object of string pairs")
    return parsed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target-id", required=True)
    parser.add_argument("--url", required=True)
    parser.add_argument("--resume", type=Path, required=True)
    parser.add_argument("--values-json", type=_mapping, required=True)
    parser.add_argument("--answers-json", type=_mapping, default={})
    parser.add_argument("--cdp-endpoint", default="http://localhost:9222")
    parser.add_argument("--command-timeout", type=float, default=6.0)
    parser.add_argument("--render-timeout", type=float, default=10.0)
    args = parser.parse_args()
    result = fill_ashby_target(
        endpoint=args.cdp_endpoint,
        target_id=args.target_id,
        url=args.url,
        resume=args.resume,
        values=args.values_json,
        answers=args.answers_json,
        command_timeout=args.command_timeout,
        render_timeout=args.render_timeout,
    )
    print("ASHBY_RAW_CDP_RESULT=" + json.dumps(asdict(result), ensure_ascii=False))
    return 0 if result.success else 1


if __name__ == "__main__":
    raise SystemExit(main())
