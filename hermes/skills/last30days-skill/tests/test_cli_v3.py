# fmt: off
import contextlib
import json
import io
import os
import shutil
import tempfile
import subprocess
import sys
import types
import unittest
from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime
from pathlib import Path
from unittest import mock

import last30days as cli
from lib import schema

REPO_ROOT = Path(__file__).resolve().parents[1]


class CliV3Tests(unittest.TestCase):
    def make_report(self, topic: str = "OpenClaw vs NanoClaw") -> schema.Report:
        return schema.Report(
            topic=topic,
            range_from="2026-02-14",
            range_to="2026-03-16",
            generated_at="2026-03-16T00:00:00+00:00",
            provider_runtime=schema.ProviderRuntime(
                reasoning_provider="gemini",
                planner_model="gemini-3.1-flash-lite",
                rerank_model="gemini-3.1-flash-lite",
            ),
            query_plan=schema.QueryPlan(
                intent="comparison",
                freshness_mode="balanced_recent",
                cluster_mode="debate",
                raw_topic=topic,
                subqueries=[
                    schema.SubQuery(
                        label="primary",
                        search_query=topic.lower(),
                        ranking_query=f"What are people saying about {topic}?",
                        sources=["grounding"],
                    )
                ],
                source_weights={"grounding": 1.0},
            ),
            clusters=[],
            ranked_candidates=[],
            items_by_source={"grounding": []},
            errors_by_source={},
        )

    def test_mock_json_cli(self):
        result = subprocess.run(
            [sys.executable, "skills/last30days/scripts/last30days.py", "test topic", "--mock", "--emit=json"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual("1.4", payload["schema_version"])
        self.assertEqual("test topic", payload["query"])
        self.assertIn("results", payload)
        self.assertIn("clusters", payload)
        self.assertIn("source_status", payload)

    def test_invalid_plan_json_exits_nonzero(self):
        """Malformed --plan JSON must fail fast, not silently fall back to the
        internal planner and burn a paid run the user did not ask for."""
        result = subprocess.run(
            [
                sys.executable,
                "skills/last30days/scripts/last30days.py",
                "test topic",
                "--mock",
                "--emit=json",
                "--plan",
                "{not valid json",
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        self.assertEqual(2, result.returncode, result.stderr)
        self.assertIn("Invalid --plan JSON", result.stderr)

    def ___LONG_STRING___(self):
        result = subprocess.run(
            [
                sys.executable,
                "skills/last30days/scripts/last30days.py",
                "test topic",
                "--mock",
                "--emit=json",
                "--plan",
                json.dumps({"queries": {"web": ["Berlin"]}}),
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        self.assertEqual(2, result.returncode, result.stderr)
        self.assertIn("Invalid --plan schema", result.stderr)
        self.assertNotIn("fallback-plan", result.stderr)

    def ___LONG_STRING___(self):
        plan_a = {
            "intent": "product",
            "freshness_mode": "balanced_recent",
            "cluster_mode": "market",
            "subqueries": [{
                "label": "primary",
                "search_query": "espresso grinders",
                "ranking_query": "Which grinders do people recommend?",
                "sources": ["grounding"],
                "weight": 1.0,
            }],
        }
        plan_b = json.loads(json.dumps(plan_a))
        plan_b["subqueries"][0]["search_query"] = "café grinders"

        def research(**kwargs):
            report = self.make_report(topic=kwargs["topic"])
            report.query_plan.subqueries = [
                schema.SubQuery(**subquery)
                for subquery in kwargs["external_plan"]["subqueries"]
            ]
            return report

        with tempfile.TemporaryDirectory() as tmp, contextlib.ExitStack() as stack:
            synthesis = Path(tmp) / "synthesis.md"
            synthesis.write_text("# Grinders\nSupported findings.\n", encoding="utf-8")
            plan_file = Path(tmp) / "plan.json"
            plan_file.write_text(json.dumps(plan_b), encoding="utf-8")
            stack.enter_context(mock.patch.dict(os.environ, {"LAST30DAYS_SKIP_PREFLIGHT": "1"}))
            stack.enter_context(mock.patch.object(cli.env, "get_config", return_value={}))
            stack.enter_context(mock.patch.object(cli.pipeline, "diagnose", return_value={}))
            stack.enter_context(mock.patch.object(cli.ui, "ProgressDisplay"))
            stack.enter_context(mock.patch.object(cli, "_show_runtime_ui"))
            runner = stack.enter_context(mock.patch.object(cli.pipeline, "run", side_effect=research))
            renderer = stack.enter_context(mock.patch.object(cli, "_render_save_and_print", return_value=0))
            cases = [
                ("-", json.dumps(plan_a), "espresso grinders", 1),
                ("-", json.dumps(plan_a, indent=2, sort_keys=True), "espresso grinders", 1),
                ("-", json.dumps(plan_b, ensure_ascii=False), "café grinders", 2),
                (json.dumps(plan_b), "", "café grinders", 2),
                (str(plan_file), "", "café grinders", 2),
            ]
            for plan_arg, raw, expected_query, expected_calls in cases:
                with self.subTest(plan=plan_arg, query=expected_query):
                    argv = [
                        "last30days.py", "espresso grinders", "--mock",
                        "--as-of", "2026-03-16", "--emit=html",
                        "--synthesis-file", str(synthesis), "--plan", plan_arg,
                    ]
                    stdin = io.StringIO(raw)
                    with mock.patch.object(sys, "argv", argv), \
                         mock.patch.object(sys, "stdin", stdin), \
                         mock.patch.object(stdin, "read", wraps=stdin.read) as read, \
                         redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                        rc = cli.main()
                    self.assertEqual(0, rc)
                    self.assertEqual(expected_calls, runner.call_count)
                    report = renderer.call_args.args[1]
                    self.assertEqual(expected_query, report.query_plan.subqueries[0].search_query)
                    self.assertEqual(1 if plan_arg == "-" else 0, read.call_count)

    def ___LONG_STRING___(self):
        self.assertEqual(
            ["grounding", "reddit", "hackernews"],
            cli.parse_search_flag("web, reddit, hn, web"),
        )

    def ___LONG_STRING___(self):
        self.assertEqual(
            ["threads", "pinterest"],
            cli.parse_search_flag("threads, pinterest"),
        )

    def ___LONG_STRING___(self):
        stderr = io.StringIO()
        with (
            mock.patch.object(sys, "argv", [
                "last30days.py", "best rust async tools",
                "--search", "telegram,tiktok", "--quick", "--web-backend", "none",
            ]),
            mock.patch.object(cli.env, "get_config", return_value={}),
            mock.patch.object(cli.pipeline, "diagnose", return_value={}),
            mock.patch.dict(os.environ, {"LAST30DAYS_SKIP_PREFLIGHT": "1"}),
            redirect_stderr(stderr),
        ):
            result = cli.main()

        self.assertEqual(2, result)
        self.assertIn(
            "None of the sources in --search can run here: telegram, tiktok",
            stderr.getvalue(),
        )
        self.assertIn("last30days.py doctor", stderr.getvalue())
        self.assertNotIn("Traceback", stderr.getvalue())

    def ___LONG_STRING___(self):
        available = cli.pipeline.available_sources(
            {"SCRAPECREATORS_API_KEY": "test-key", "INCLUDE_SOURCES": ""},
            requested_sources=["threads"],
        )
        self.assertIn("threads", available)

    def ___LONG_STRING___(self):
        available = cli.pipeline.available_sources(
            {"OPENROUTER_API_KEY": "test-key", "INCLUDE_SOURCES": ""},
            requested_sources=["perplexity"],
        )
        self.assertIn("perplexity", available)

    def ___LONG_STRING___(self):
        available = cli.pipeline.available_sources(
            {"PERPLEXITY_API_KEY": "test-key", "INCLUDE_SOURCES": ""},
            requested_sources=["perplexity"],
        )
        self.assertIn("perplexity", available)

    def ___LONG_STRING___(self):
        with self.assertRaises(SystemExit):
            cli.parse_search_flag("unknown")
        with self.assertRaises(SystemExit):
            cli.parse_search_flag(" , ")

    def ___LONG_STRING___(self):
        sources = cli.resolve_requested_sources(
            "reddit", {"LAST30DAYS_DEFAULT_SEARCH": "x,youtube"},
        )
        self.assertEqual(["reddit"], sources)

    def ___LONG_STRING___(self):
        sources = cli.resolve_requested_sources(
            None, {"LAST30DAYS_DEFAULT_SEARCH": "web, reddit, hn"},
        )
        self.assertEqual(["grounding", "reddit", "hackernews"], sources)

    def ___LONG_STRING___(self):
        self.assertIsNone(cli.resolve_requested_sources(None, {}))
        self.assertIsNone(
            cli.resolve_requested_sources(None, {"LAST30DAYS_DEFAULT_SEARCH": ""})
        )
        self.assertIsNone(
            cli.resolve_requested_sources(None, {"LAST30DAYS_DEFAULT_SEARCH": "  "})
        )

    def ___LONG_STRING___(self):
        with self.assertRaises(SystemExit) as exc:
            cli.resolve_requested_sources(
                None, {"LAST30DAYS_DEFAULT_SEARCH": "notasource"},
            )
        self.assertIn("LAST30DAYS_DEFAULT_SEARCH", str(exc.exception))

    def ___LONG_STRING___(self):
        self.assertIsNone(cli.add_deep_research_source(None))

    def ___LONG_STRING___(self):
        self.assertEqual(
            ["reddit", "perplexity"],
            cli.add_deep_research_source(["reddit"]),
        )
        self.assertEqual(
            ["reddit", "perplexity"],
            cli.add_deep_research_source(["reddit", "perplexity"]),
        )

    def ___LONG_STRING___(self):
        config = {"INCLUDE_SOURCES": "notperplexity,reddit"}

        cli.enable_deep_research_source(config)

        self.assertEqual(
            ["notperplexity", "reddit", "perplexity"],
            config["INCLUDE_SOURCES"].split(","),
        )

    def ___LONG_STRING___(self):
        config = {"EXCLUDE_SOURCES": "reddit,Perplexity"}

        with self.assertRaisesRegex(
            ValueError,
            "conflicts with EXCLUDE_SOURCES=perplexity",
        ):
            cli.enable_deep_research_source(config)

    def ___LONG_STRING___(self):
        parser = cli.build_parser()
        args, extra = parser.parse_known_args(["--days", "7", "biosecurity", "ai", "agents"])
        self.assertEqual(7, args.lookback_days)
        self.assertEqual(["biosecurity", "ai", "agents"], args.topic)
        self.assertEqual([], extra)

    def ___LONG_STRING___(self):
        """Regression for #905: CONFIGURATION.md documents --web-backend=keyless
        to force the zero-key floor, but the choices list rejected it."""
        parser = cli.build_parser()
        args, extra = parser.parse_known_args(["--web-backend", "keyless", "biosecurity"])
        self.assertEqual("keyless", args.web_backend)
        self.assertEqual([], extra)

    def ___LONG_STRING___(self):
        parser = cli.build_parser()
        action = next(
            candidate
            for candidate in parser._actions
            if "--deep-research" in candidate.option_strings
        )
        self.assertIn("PERPLEXITY_API_KEY", action.help)
        self.assertIn("OPENROUTER_API_KEY", action.help)
        self.assertIn("cannot be combined with competitor or vs-mode", action.help)

    def ___LONG_STRING___(self):
        for argv in (
            ["last30days.py", "--discover", "agents", "--deep-research"],
            ["last30days.py", "--drill", "cluster-1", "--deep-research"],
        ):
            with self.subTest(argv=argv), mock.patch.object(
                cli.env,
                "get_config",
                return_value={},
            ), mock.patch.object(
                cli,
                "_run_discover",
            ) as discover_mock, mock.patch.object(
                cli,
                "_run_drill",
            ) as drill_mock, mock.patch.dict(
                os.environ,
                {"LAST30DAYS_SKIP_PREFLIGHT": "1"},
                clear=False,
            ), mock.patch.object(sys, "argv", argv):
                stderr = io.StringIO()
                with redirect_stderr(stderr):
                    rc = cli.main()

            self.assertEqual(2, rc)
            discover_mock.assert_not_called()
            drill_mock.assert_not_called()
            self.assertIn("requires a normal positional topic", stderr.getvalue())

    def ___LONG_STRING___(self):
        diag = {
            "available_sources": ["perplexity"],
            "providers": {"google": False, "openai": False, "xai": False},
            "x_backend": None,
            "bird_installed": True,
            "bird_authenticated": False,
            "bird_username": None,
            "native_web_backend": None,
        }
        with mock.patch.object(
            cli.env,
            "get_config",
            return_value={"PERPLEXITY_API_KEY": "pplx-test"},
        ), mock.patch.object(
            cli.pipeline,
            "diagnose",
            return_value=diag,
        ) as diagnose_mock, mock.patch.object(
            cli.pipeline,
            "run",
        ) as run_mock, mock.patch.object(
            cli.ui,
            "ProgressDisplay",
            return_value=mock.Mock(),
        ), mock.patch.object(
            sys,
            "argv",
            [
                "last30days.py",
                "Alpha",
                "vs",
                "Beta",
                "--mock",
                "--deep-research",
            ],
        ):
            stderr = io.StringIO()
            with redirect_stderr(stderr):
                rc = cli.main()

        self.assertEqual(2, rc)
        diagnose_mock.assert_not_called()
        run_mock.assert_not_called()
        self.assertIn(
            "one paid Deep Research run per user action",
            stderr.getvalue(),
        )

    def ___LONG_STRING___(self):
        report = self.make_report(topic="why AI safety matters")
        diag = {
            "available_sources": ["reddit", "perplexity"],
            "providers": {"google": False, "openai": False, "xai": False},
            "x_backend": None,
            "bird_installed": True,
            "bird_authenticated": False,
            "bird_username": None,
            "native_web_backend": None,
        }
        with mock.patch.object(
            cli.env,
            "get_config",
            return_value={"OPENROUTER_API_KEY": "openrouter-test"},
        ), mock.patch.object(
            cli.env,
            "read_secret_env",
            return_value="hosted-test-key",
        ), mock.patch.object(
            cli.pipeline,
            "diagnose",
            return_value=diag,
        ), mock.patch.object(
            cli.pipeline,
            "run",
            return_value=report,
        ) as run_mock, mock.patch(
            "lib.hosted.run_hosted",
        ) as hosted_mock, mock.patch.object(
            cli.ui,
            "ProgressDisplay",
            return_value=mock.Mock(),
        ), mock.patch.object(
            cli,
            "emit_output",
            return_value="# rendered",
        ), mock.patch.dict(
            os.environ,
            {
                "LAST30DAYS_API_BASE": "https://hosted.example.test",
                "LAST30DAYS_SKIP_PREFLIGHT": "1",
            },
            clear=False,
        ), mock.patch.object(
            sys,
            "argv",
            [
                "last30days.py",
                "why",
                "AI",
                "safety",
                "matters",
                "--deep-research",
                "--search",
                "reddit",
            ],
        ):
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                rc = cli.main()

        self.assertEqual(0, rc)
        hosted_mock.assert_not_called()
        requested_sources = run_mock.call_args.kwargs["requested_sources"]
        self.assertEqual(["reddit", "perplexity"], requested_sources)
        self.assertTrue(run_mock.call_args.kwargs["config"]["_deep_research"])

    def _run_perplexity_search_type_cli(self, argv_extra, config, *, hosted):
        report = self.make_report(topic="rust releases")
        diag = {
            "available_sources": ["reddit"],
            "providers": {"google": False, "openai": False, "xai": False},
            "x_backend": None,
            "bird_installed": True,
            "bird_authenticated": False,
            "bird_username": None,
            "native_web_backend": None,
        }
        environ = {"LAST30DAYS_SKIP_PREFLIGHT": "1"}
        if hosted:
            environ["LAST30DAYS_API_BASE"] = "https://hosted.example.test"
        stderr = io.StringIO()
        with mock.patch.object(
            cli.env, "get_config", return_value=dict(config),
        ), mock.patch.object(
            cli.env, "read_secret_env",
            return_value="hosted-test-key" if hosted else None,
        ), mock.patch.object(
            cli.pipeline, "diagnose", return_value=diag,
        ), mock.patch.object(
            cli.pipeline, "run", return_value=report,
        ) as run_mock, mock.patch(
            "lib.hosted.run_hosted", return_value=0,
        ) as hosted_mock, mock.patch(
            "lib.resolve.auto_resolve", return_value={},
        ), mock.patch.object(
            cli.ui, "ProgressDisplay", return_value=mock.Mock(),
        ), mock.patch.object(
            cli, "emit_output", return_value="# rendered",
        ), mock.patch.dict(
            os.environ, environ, clear=False,
        ), mock.patch.object(
            sys, "argv", ["last30days.py", "rust", "releases", *argv_extra],
        ):
            if not hosted:
                os.environ.pop("LAST30DAYS_API_BASE", None)
            with redirect_stdout(io.StringIO()), redirect_stderr(stderr):
                rc = cli.main()
        return rc, run_mock, hosted_mock, stderr.getvalue()

    def ___LONG_STRING___(self):
        rc, run_mock, hosted_mock, err = self._run_perplexity_search_type_cli(
            ["--perplexity-search-type", "fast"],
            {"PERPLEXITY_API_KEY": "pplx-test"},
            hosted=True,
        )

        self.assertEqual(0, rc)
        hosted_mock.assert_not_called()
        run_mock.assert_called_once()
        config = run_mock.call_args.kwargs["config"]
        self.assertEqual("fast", config["LAST30DAYS_PERPLEXITY_SEARCH_TYPE"])
        self.assertEqual(1, err.count("--perplexity-search-type"))
        self.assertIn("bypassing the hosted backend", err)
        self.assertNotIn("does not apply LAST30DAYS_PERPLEXITY_SEARCH_TYPE", err)

    def ___LONG_STRING___(self):
        rc, run_mock, hosted_mock, err = self._run_perplexity_search_type_cli(
            ["--perplexity-search-type", "fast"],
            {"OPENROUTER_API_KEY": "or-test"},
            hosted=True,
        )

        self.assertEqual(0, rc)
        hosted_mock.assert_called_once()
        run_mock.assert_not_called()
        self.assertEqual(1, err.count("no direct PERPLEXITY_API_KEY is configured"))
        self.assertNotIn("bypassing the hosted backend", err)

    def ___LONG_STRING___(self):
        # Without a direct key the flag cannot apply, so hosted routing and its
        # local-only option checks must match a run without the flag.
        for extra in (["--x-posts", "https://x.com/a/status/1"], ["--emit=json", "--json-profile=agent"]):
            plain_rc, plain_run, plain_hosted, _ = self._run_perplexity_search_type_cli(
                extra, {"OPENROUTER_API_KEY": "or-test"}, hosted=True,
            )
            flag_rc, flag_run, flag_hosted, _ = self._run_perplexity_search_type_cli(
                ["--perplexity-search-type", "fast", *extra],
                {"OPENROUTER_API_KEY": "or-test"},
                hosted=True,
            )
            self.assertEqual(plain_rc, flag_rc, extra)
            self.assertEqual(plain_run.call_count, flag_run.call_count, extra)
            self.assertEqual(plain_hosted.call_count, flag_hosted.call_count, extra)

    def ___LONG_STRING___(self):
        rc, run_mock, hosted_mock, err = self._run_perplexity_search_type_cli(
            [], {"LAST30DAYS_PERPLEXITY_SEARCH_TYPE": "fast"}, hosted=True,
        )

        self.assertEqual(0, rc)
        hosted_mock.assert_called_once()
        run_mock.assert_not_called()
        self.assertEqual(
            1,
            err.count("hosted backend does not apply LAST30DAYS_PERPLEXITY_SEARCH_TYPE"),
        )
        self.assertNotIn("bypassing the hosted backend", err)

    def ___LONG_STRING___(self):
        rc, run_mock, hosted_mock, err = self._run_perplexity_search_type_cli(
            [], {}, hosted=True,
        )

        self.assertEqual(0, rc)
        hosted_mock.assert_called_once()
        run_mock.assert_not_called()
        self.assertNotIn("search type", err.lower())
        self.assertNotIn("SEARCH_TYPE", err)

    def ___LONG_STRING___(self):
        _, baseline_run, _, _ = self._run_perplexity_search_type_cli(
            [], {"PERPLEXITY_API_KEY": "pplx-test"}, hosted=False,
        )
        rc, flagged_run, _, err = self._run_perplexity_search_type_cli(
            ["--perplexity-search-type", "fast"],
            {"PERPLEXITY_API_KEY": "pplx-test"},
            hosted=False,
        )

        self.assertEqual(0, rc)
        self.assertEqual(
            baseline_run.call_args.kwargs["requested_sources"],
            flagged_run.call_args.kwargs["requested_sources"],
        )
        self.assertNotIn("perplexity", flagged_run.call_args.kwargs["requested_sources"] or [])
        config = flagged_run.call_args.kwargs["config"]
        self.assertEqual("fast", config["LAST30DAYS_PERPLEXITY_SEARCH_TYPE"])
        self.assertNotIn("INCLUDE_SOURCES", config)
        self.assertNotIn("bypassing the hosted backend", err)

    def ___LONG_STRING___(self):
        _, run_mock, _, _ = self._run_perplexity_search_type_cli(
            ["--perplexity-search-type", "web"],
            {"LAST30DAYS_PERPLEXITY_SEARCH_TYPE": "fast"},
            hosted=False,
        )

        config = run_mock.call_args.kwargs["config"]
        self.assertEqual("web", config["LAST30DAYS_PERPLEXITY_SEARCH_TYPE"])

    def ___LONG_STRING___(self):
        parser = cli.build_parser()
        for value in ("auto", "brave", "exa", "serper", "parallel", "parallel-mcp", "none"):
            args, extra = parser.parse_known_args(["--web-backend", value, "biosecurity"])
            self.assertEqual(value, args.web_backend)
            self.assertEqual([], extra)

    def ___LONG_STRING___(self):
        parser = cli.build_parser()
        with self.assertRaises(SystemExit):
            parser.parse_known_args(["--web-backend", "bogus", "biosecurity"])

    def ___LONG_STRING___(self):
        parser = cli.build_parser()
        args, extra = parser.parse_known_args(
            ["--emit", "json", "--output", "results/run.json", "biosecurity"]
        )
        self.assertEqual("results/run.json", args.output)
        self.assertEqual(["biosecurity"], args.topic)
        self.assertEqual([], extra)

    def ___LONG_STRING___(self):
        parser = cli.build_parser()
        args, extra = parser.parse_known_args(
            ["--max-results", "200", "--max-per-source", "60",
             "--max-source-fetches", "8", "figma config 2026"]
        )
        self.assertEqual(200, args.max_results)
        self.assertEqual(60, args.max_per_source)
        self.assertEqual(8, args.max_source_fetches)
        self.assertEqual(["figma config 2026"], args.topic)
        self.assertEqual([], extra)

    def ___LONG_STRING___(self):
        parser = cli.build_parser()
        args, _ = parser.parse_known_args(["figma config 2026"])
        self.assertIsNone(args.max_results)
        self.assertIsNone(args.max_per_source)
        self.assertIsNone(args.max_source_fetches)

    def ___LONG_STRING___(self):
        with mock.patch.object(
            cli.env, "get_config", side_effect=AssertionError("config should not load")
        ), mock.patch.object(sys, "argv", ["last30days.py", "topic", "--save"]):
            stderr = io.StringIO()
            with redirect_stderr(stderr), self.assertRaises(SystemExit) as exc:
                cli.main()
        self.assertEqual(2, exc.exception.code)
        self.assertIn("--save", stderr.getvalue())

    def ___LONG_STRING___(self):
        with mock.patch.object(
            cli.env, "get_config", side_effect=AssertionError("config should not load")
        ), mock.patch.object(sys, "argv", ["last30days.py", "topic", "--agent"]):
            stderr = io.StringIO()
            with redirect_stderr(stderr), self.assertRaises(SystemExit) as exc:
                cli.main()
        self.assertEqual(2, exc.exception.code)
        self.assertIn("skill arguments", stderr.getvalue())

    def ___LONG_STRING___(self):
        with mock.patch.object(
            cli.env, "get_config", side_effect=AssertionError("config should not load")
        ), mock.patch.object(sys, "argv", ["last30days.py", "topic", "--agent", "--save"]):
            stderr = io.StringIO()
            with redirect_stderr(stderr), self.assertRaises(SystemExit) as exc:
                cli.main()
        self.assertEqual(2, exc.exception.code)
        message = stderr.getvalue()
        self.assertIn("--agent", message)
        self.assertIn("--save", message)

    def ___LONG_STRING___(self):
        with mock.patch.object(cli.env, "get_config", return_value={}), \
             mock.patch("lib.setup_wizard.run_github_auth", return_value={"status": "cancelled"}), \
             mock.patch.object(sys, "argv", ["last30days.py", "setup", "--github"]):
            stdout = io.StringIO()
            stderr = io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                rc = cli.main()
        self.assertEqual(0, rc)

    def ___LONG_STRING___(self):
        with mock.patch.object(
            cli.env, "get_config", side_effect=AssertionError("config should not load")
        ), mock.patch.object(sys, "argv", ["last30days.py", "setup", "--bad"]):
            stderr = io.StringIO()
            with redirect_stderr(stderr), self.assertRaises(SystemExit) as exc:
                cli.main()
        self.assertEqual(2, exc.exception.code)
        self.assertIn("--bad", stderr.getvalue())

    def ___LONG_STRING___(self):
        stderr = io.StringIO()
        with redirect_stderr(stderr):
            with self.assertRaises(SystemExit) as exc:
                cli.ensure_supported_python((3, 9, 6))
        self.assertEqual(1, exc.exception.code)
        message = stderr.getvalue()
        self.assertIn("last30days v4 requires Python 3.12+", message)
        self.assertIn("Detected Python 3.9.6", message)
        self.assertIn("python3.12", message)

    def ___LONG_STRING___(self):
        cli.ensure_supported_python((3, 12, 0))

    def ___LONG_STRING___(self):
        self.assertEqual(
            "reddit",
            cli._missing_sources_for_promo({"available_sources": ["youtube"]}),
        )
        self.assertEqual(
            "web",
            cli._missing_sources_for_promo({"available_sources": ["reddit", "x"]}),
        )
        # The web promo is satisfied by a paid backend (better web search), not
        # by the keyless grounding floor — keyless web is always available now.
        self.assertIsNone(
            cli._missing_sources_for_promo(
                {"available_sources": ["reddit", "x", "grounding"], "native_web_backend": "brave"}
            ),
        )

    def ___LONG_STRING___(self):
        note = cli._optional_x_omission_text(
            {"available_sources": ["reddit", "youtube", "grounding"]},
            None,
        )
        self.assertEqual(
            "Optional source omitted: X/Twitter was not enabled; research "
            "continued with the available sources.",
            note,
        )

    def ___LONG_STRING___(self):
        self.assertIsNone(
            cli._optional_x_omission_text(
                {"available_sources": ["reddit", "x", "youtube"]},
                None,
            )
        )
        self.assertIsNone(
            cli._optional_x_omission_text(
                {"available_sources": ["reddit", "youtube"]},
                ["reddit", "youtube"],
            )
        )
        # ...or suppressed entirely on a native-search host.
        self.assertIsNone(
            cli._missing_sources_for_promo(
                {"available_sources": ["reddit", "x", "grounding"], "native_search": True}
            ),
        )

    def ___LONG_STRING___(self):
        report = self.make_report()
        self.assertEqual("openclaw-vs-nanoclaw", cli.slugify(report.topic))
        self.assertEqual("last30days CLI.", cli.__doc__)

        compact = cli.emit_output(report, "compact")
        json_output = cli.emit_output(report, "json")
        context = cli.emit_output(report, "context")
        brief = cli.emit_output(report, "brief")

        self.assertIn("# last30days v", compact)
        self.assertIn('"query": "OpenClaw vs NanoClaw"', json_output)
        self.assertIsInstance(context, str)
        self.assertIn("# Production Brief:", brief)

        with self.assertRaises(SystemExit):
            cli.emit_output(report, "bad-mode")

    def ___LONG_STRING___(self):
        report = self.make_report()
        with tempfile.TemporaryDirectory() as tmp:
            path = cli.save_output(report, "json", tmp)
            self.assertEqual(".json", path.suffix)
            payload = json.loads(path.read_text())
            self.assertEqual("OpenClaw vs NanoClaw", payload["query"])

    def ___LONG_STRING___(self):
        """A --emit=compact --save-dir run must save the complete debug
        artifact (all clusters plus per-source items), not the compact stdout
        render. Saving the compact render made most collected evidence
        unrecoverable from the raw file (#923)."""
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                [
                    sys.executable,
                    "skills/last30days/scripts/last30days.py",
                    "compact save probe",
                    "--mock",
                    "--emit=compact",
                    f"--save-dir={tmp}",
                ],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            saved = list(Path(tmp).glob("*.md"))
            self.assertEqual(1, len(saved), saved)
            content = saved[0].read_text(encoding="utf-8")
            self.assertIn("## All Items by Source", content)
            self.assertNotIn("## All Items by Source", result.stdout)

    def ___LONG_STRING___(self):
        report = self.make_report()
        with tempfile.TemporaryDirectory() as tmp:
            save_dir = Path(tmp)
            today = datetime.now().strftime("%Y-%m-%d")
            base = save_dir / "openclaw-vs-nanoclaw-raw.md"
            dated = save_dir / f"openclaw-vs-nanoclaw-raw-{today}.md"
            base.write_text("base content", encoding="utf-8")
            dated.write_text("dated content", encoding="utf-8")

            saved = cli.save_output(report, "md", tmp)

            self.assertEqual((save_dir / f"openclaw-vs-nanoclaw-raw-{today}-1.md").resolve(), saved)
            self.assertEqual("base content", base.read_text(encoding="utf-8"))
            self.assertEqual("dated content", dated.read_text(encoding="utf-8"))
            self.assertTrue(saved.exists())

    def ___LONG_STRING___(self):
        from lib import render as render_module

        report = self.make_report()
        with tempfile.TemporaryDirectory() as tmp:
            save_dir = Path(tmp)
            today = datetime.now().strftime("%Y-%m-%d")
            base = save_dir / "openclaw-vs-nanoclaw-raw.md"
            dated = save_dir / f"openclaw-vs-nanoclaw-raw-{today}.md"
            base.write_text("base content", encoding="utf-8")
            dated.write_text("dated content", encoding="utf-8")

            def render_fn(actual_path: Path) -> str:
                return render_module.render_compact(report, save_path=str(actual_path))

            saved = cli.save_output(report, "md", tmp, render_fn=render_fn)

            expected = (save_dir / f"openclaw-vs-nanoclaw-raw-{today}-1.md").resolve()
            self.assertEqual(expected, saved.resolve())
            content = saved.read_text(encoding="utf-8")
            self.assertIn(f"Raw results saved to {saved}", content)
            self.assertNotIn(f"Raw results saved to {base}", content)
            self.assertNotIn(f"Raw results saved to {dated}", content)
            self.assertEqual("base content", base.read_text(encoding="utf-8"))
            self.assertEqual("dated content", dated.read_text(encoding="utf-8"))

    def ___LONG_STRING___(self):
        report = self.make_report()
        with tempfile.TemporaryDirectory() as tmp:
            save_dir = Path(tmp)

            def fail_render(_actual_path: Path) -> str:
                raise RuntimeError("render failed")

            with self.assertRaisesRegex(RuntimeError, "render failed"):
                cli.save_output(report, "md", tmp, render_fn=fail_render)

            self.assertEqual([], list(save_dir.iterdir()))

    def ___LONG_STRING___(self):
        report = self.make_report(topic="Collision Topic")
        with tempfile.TemporaryDirectory() as tmp:
            save_dir = Path(tmp)
            today = datetime.now().strftime("%Y-%m-%d")
            base = save_dir / "collision-topic-raw.md"
            dated = save_dir / f"collision-topic-raw-{today}.md"
            expected = save_dir / f"collision-topic-raw-{today}-1.md"
            base.write_text("base content", encoding="utf-8")
            dated.write_text("dated content", encoding="utf-8")
            args = types.SimpleNamespace(
                topic=["Collision Topic"],
                competitors=None,
                competitors_list=None,
                competitors_plan=None,
                drill=False,
                register=None,
                emit="compact",
                output=None,
                save_dir=str(save_dir),
                save_suffix="",
                json_profile="agent",
                publish_html=False,
            )
            stdout = io.StringIO()
            stderr = io.StringIO()

            with redirect_stdout(stdout), redirect_stderr(stderr):
                rc = cli._render_save_and_print(args, report, None, None, {})

            self.assertEqual(0, rc)
            expected_display = cli.compute_output_path_display(str(expected))
            footer = f"Raw results saved to {expected_display}"
            self.assertTrue(expected.exists())
            self.assertIn(footer, expected.read_text(encoding="utf-8"))
            self.assertIn(footer, stdout.getvalue())
            self.assertEqual("base content", base.read_text(encoding="utf-8"))
            self.assertEqual("dated content", dated.read_text(encoding="utf-8"))

    def ___LONG_STRING___(self):
        report = self.make_report()
        with tempfile.TemporaryDirectory() as tmp:
            path = cli.save_output(report, "md", tmp)
            raw = path.read_bytes()
            content = path.read_text(encoding="utf-8")
        self.assertIn(report.topic, content)
        # Verify the raw bytes decode cleanly as UTF-8.
        self.assertEqual(content, raw.decode("utf-8"))

    def ___LONG_STRING___(self):
        with tempfile.TemporaryDirectory() as tmp:
            out_path = Path(tmp) / "nested" / "results.json"
            saved = cli.save_rendered_output('{"ok": true}', str(out_path))
            self.assertEqual(out_path.resolve(), saved)
            self.assertEqual('{"ok": true}', out_path.read_text(encoding="utf-8"))

    def ___LONG_STRING___(self):
        # Regression: f"~/{relative}" stringified pathlib.Path with the
        # OS-native separator, producing "~/Documents\\Last30Days\\..." on
        # Windows that no shell or File Explorer could open. The fix is
        # f"~/{relative.as_posix()}" which forces forward slashes regardless
        # of host OS. On POSIX hosts this asserts the contract for
        # cross-platform safety; on Windows hosts it would fail without the fix.
        real_home = Path.home()
        tmp_under_home = Path(tempfile.mkdtemp(prefix="l30d_save_path_", dir=str(real_home)))
        try:
            save_dir = tmp_under_home / "Documents" / "Last30Days"
            save_dir.mkdir(parents=True, exist_ok=True)
            display = cli.compute_save_path_display(
                str(save_dir), "british airways middle east", "v3", "compact"
            )
            self.assertTrue(display.startswith("~/"), f"Expected '~/' prefix, got: {display}")
            self.assertNotIn("\\", display, f"Backslash leaked into display: {display}")
            self.assertTrue(
                display.endswith("british-airways-middle-east-raw-v3.md"),
                f"Expected slug+suffix at end, got: {display}",
            )
        finally:
            shutil.rmtree(tmp_under_home, ignore_errors=True)

    def ___LONG_STRING___(self):
        real_home = Path.home()
        tmp_under_home = Path(tempfile.mkdtemp(prefix="l30d_output_path_", dir=str(real_home)))
        try:
            output_path = tmp_under_home / "Documents" / "Last30Days" / "run.json"
            display = cli.compute_output_path_display(str(output_path))
            self.assertTrue(display.startswith("~/"), f"Expected '~/' prefix, got: {display}")
            self.assertNotIn("\\", display, f"Backslash leaked into display: {display}")
            self.assertTrue(display.endswith("Documents/Last30Days/run.json"), display)
        finally:
            shutil.rmtree(tmp_under_home, ignore_errors=True)

    def ___LONG_STRING___(self):
        report = self.make_report()

        success_store = types.SimpleNamespace(
            scoped_db=lambda _path: contextlib.nullcontext(),
            init_db=mock.Mock(),
            add_topic=mock.Mock(return_value={"id": 7}),
            record_run=mock.Mock(return_value=11),
            findings_from_report=mock.Mock(return_value=[{"title": "x"}]),
            store_findings=mock.Mock(return_value={"new": 2, "updated": 1}),
            update_run=mock.Mock(),
        )
        with mock.patch.dict(sys.modules, {"store": success_store}):
            counts = cli.persist_report(report)
        self.assertEqual({"new": 2, "updated": 1}, counts)
        success_store.update_run.assert_called_once_with(
            11,
            status="completed",
            findings_new=2,
            findings_updated=1,
        )

        failure_store = types.SimpleNamespace(
            scoped_db=lambda _path: contextlib.nullcontext(),
            init_db=mock.Mock(),
            add_topic=mock.Mock(return_value={"id": 7}),
            record_run=mock.Mock(return_value=12),
            findings_from_report=mock.Mock(side_effect=RuntimeError("boom")),
            store_findings=mock.Mock(),
            update_run=mock.Mock(),
        )
        with mock.patch.dict(sys.modules, {"store": failure_store}):
            with self.assertRaises(RuntimeError):
                cli.persist_report(report)
        failure_store.update_run.assert_called_once()
        _, kwargs = failure_store.update_run.call_args
        self.assertEqual("failed", kwargs["status"])
        self.assertIn("boom", kwargs["error_message"])

    def ___LONG_STRING___(self):
        report = self.make_report()
        diag = {
            "available_sources": ["grounding", "youtube"],
            "providers": {"google": True, "openai": False, "xai": False},
            "x_backend": None,
            "bird_installed": True,
            "bird_authenticated": False,
            "bird_username": None,
            "native_web_backend": "brave",
        }
        fake_progress = mock.Mock()
        with mock.patch.object(cli.env, "get_config", return_value={}), \
             mock.patch.object(cli.pipeline, "diagnose", return_value=diag), \
             mock.patch.object(cli.pipeline, "run", return_value=report), \
             mock.patch.object(cli.ui, "show_diagnostic_banner") as banner, \
             mock.patch.object(cli.ui, "ProgressDisplay", return_value=fake_progress) as progress_cls, \
             mock.patch.object(cli, "emit_output", return_value="# rendered"), \
             mock.patch.object(sys, "argv", ["last30days.py", "test", "topic"]):
            stdout = io.StringIO()
            stderr = io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                rc = cli.main()
        self.assertEqual(0, rc)
        banner.assert_not_called()  # Banner moved to post-research
        progress_cls.assert_called_once_with("test topic", show_banner=True)
        fake_progress.start_processing.assert_called_once()
        fake_progress.end_processing.assert_called_once()
        fake_progress.show_complete.assert_called_once_with(
            source_counts={"grounding": 0},
            display_sources=["grounding"],
        )
        fake_progress.show_promo.assert_called_once_with("reddit", diag=diag)
        self.assertIn("# rendered", stdout.getvalue())

    def ___LONG_STRING___(self):
        report = self.make_report()
        diag = {
            "available_sources": ["grounding"],
            "providers": {"google": True, "openai": False, "xai": False},
            "x_backend": None,
            "bird_installed": True,
            "bird_authenticated": False,
            "bird_username": None,
            "native_web_backend": "brave",
        }
        with tempfile.TemporaryDirectory() as tmp:
            output_path = Path(tmp) / "exports" / "run.json"
            with mock.patch.object(cli.env, "get_config", return_value={}), \
                 mock.patch.object(cli.pipeline, "diagnose", return_value=diag), \
                 mock.patch.object(cli.pipeline, "run", return_value=report), \
                 mock.patch.object(cli, "emit_output", return_value='{"rendered": true}') as emit, \
                 mock.patch.object(sys, "argv", [
                     "last30days.py",
                     "test",
                     "topic",
                     "--emit=json",
                     "--output",
                     str(output_path),
                 ]):
                stdout = io.StringIO()
                stderr = io.StringIO()
                with redirect_stdout(stdout), redirect_stderr(stderr):
                    rc = cli.main()
            self.assertEqual(0, rc)
            emit.assert_called_once()
            self.assertEqual('{"rendered": true}\n', stdout.getvalue())
            self.assertEqual('{"rendered": true}', output_path.read_text(encoding="utf-8"))
            self.assertIn(f"[last30days] Saved output to {output_path.resolve()}", stderr.getvalue())

    def ___LONG_STRING___(self):
        diag = {
            "available_sources": ["grounding"],
            "providers": {"google": True, "openai": False, "xai": False},
            "x_backend": None,
            "bird_installed": True,
            "bird_authenticated": False,
            "bird_username": None,
            "native_web_backend": "brave",
        }
        fake_progress = mock.Mock()

        def run_report(*_args, **kwargs):
            return self.make_report(topic=kwargs["topic"])

        with tempfile.TemporaryDirectory() as tmp:
            output_path = Path(tmp) / "exports" / "comparison.html"
            save_dir = Path(tmp) / "saved"
            with mock.patch.object(cli.env, "get_config", return_value={}), \
                 mock.patch.object(cli.pipeline, "diagnose", return_value=diag), \
                 mock.patch.object(cli.pipeline, "run", side_effect=run_report), \
                 mock.patch.object(cli.ui, "ProgressDisplay", return_value=fake_progress), \
                 mock.patch.object(
                     cli, "emit_comparison_output", return_value="<html>comparison</html>"
                 ) as emit_comparison, \
                 mock.patch.object(cli, "emit_output", return_value="<html>peer</html>"), \
                 mock.patch.object(sys, "argv", [
                     "last30days.py",
                     "Alpha",
                     "vs",
                     "Beta",
                     "--mock",
                     "--emit=html",
                     "--output",
                     str(output_path),
                     "--save-dir",
                     str(save_dir),
                 ]):
                stdout = io.StringIO()
                stderr = io.StringIO()
                with redirect_stdout(stdout), redirect_stderr(stderr):
                    rc = cli.main()

            self.assertEqual(0, rc)
            output_display = cli.compute_output_path_display(str(output_path))
            comparison_saved = save_dir / "alpha-vs-beta-raw-html.html"
            self.assertEqual(2, emit_comparison.call_count)
            first_kwargs = emit_comparison.call_args_list[0].kwargs
            second_kwargs = emit_comparison.call_args_list[1].kwargs
            self.assertEqual(output_display, first_kwargs["save_path"])
            comparison_display = cli.compute_output_path_display(str(comparison_saved))
            self.assertEqual(comparison_display, second_kwargs["save_path"])
            self.assertEqual("<html>comparison</html>\n", stdout.getvalue())
            self.assertEqual("<html>comparison</html>", output_path.read_text(encoding="utf-8"))
            self.assertEqual(
                "<html>comparison</html>",
                comparison_saved.read_text(encoding="utf-8"),
            )
            peer_saved = save_dir / "beta-raw-html.html"
            self.assertEqual("<html>peer</html>", peer_saved.read_text(encoding="utf-8"))
            self.assertIn(f"[last30days] Saved output to {output_path.resolve()}", stderr.getvalue())
            self.assertIn(f"[last30days] Saved output to {comparison_saved.resolve()}", stderr.getvalue())
            self.assertIn(f"[last30days] Saved output to {peer_saved.resolve()}", stderr.getvalue())
            self.assertIn(
                f"[last30days] Comparison artifact set: main={comparison_saved.resolve()}; "
                f"peers={peer_saved.resolve()}",
                stderr.getvalue(),
            )

    def ___LONG_STRING___(self):
        report = self.make_report()
        diag = {
            "available_sources": ["grounding"],
            "providers": {"google": True, "openai": False, "xai": False},
            "x_backend": None,
            "bird_installed": True,
            "bird_authenticated": False,
            "bird_username": None,
            "native_web_backend": "brave",
        }
        with mock.patch.object(cli.env, "get_config", return_value={}), \
             mock.patch.object(cli.pipeline, "diagnose", return_value=diag), \
             mock.patch.object(cli.pipeline, "run", return_value=report) as run_mock, \
             mock.patch.object(cli, "emit_output", return_value="# rendered"), \
             mock.patch.object(sys, "argv", [
                 "last30days.py",
                 "claude",
                 "code",
                 "vs",
                 "codex",
                 "--github-repo",
                 "openai/codex,anthropics/claude-code-action",
             ]):
            stdout = io.StringIO()
            stderr = io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                rc = cli.main()
        self.assertEqual(0, rc)
        # In vs-mode main + competitors run in parallel via ThreadPoolExecutor,
        # so the order of pipeline.run invocations is non-deterministic. Find
        # the main runner's call by predicate on the canonicalized github_repos
        # rather than by index.
        expected_repos = ["openai/codex", "anthropics/claude-code"]
        main_call = next(
            (c for c in run_mock.call_args_list if c.kwargs.get("github_repos") == expected_repos),
            None,
        )
        self.assertIsNotNone(
            main_call,
            f"No pipeline.run call had github_repos={expected_repos}; "
            f"saw {[c.kwargs.get('github_repos') for c in run_mock.call_args_list]}",
        )
        self.assertIn("[GitHub] Canonicalized repos:", stderr.getvalue())

    def ___LONG_STRING___(self):
        """The user-set flag must reach pipeline.run verbatim with
        provenance user-set (is_hint False) on the single-topic path."""
        report = self.make_report()
        diag = {
            "available_sources": ["grounding"],
            "providers": {"google": True, "openai": False, "xai": False},
            "x_backend": None,
            "bird_installed": True,
            "bird_authenticated": False,
            "bird_username": None,
            "native_web_backend": "brave",
        }
        with mock.patch.object(cli.env, "get_config", return_value={}), \
             mock.patch.object(cli.pipeline, "diagnose", return_value=diag), \
             mock.patch.object(cli.pipeline, "run", return_value=report) as run_mock, \
             mock.patch.object(cli, "emit_output", return_value="# rendered"), \
             mock.patch.object(sys, "argv", [
                 "last30days.py",
                 "ThriftBooks",
                 "--trustpilot-domain",
                 "www.thriftbooks.com",
             ]):
            stdout = io.StringIO()
            stderr = io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                rc = cli.main()
        self.assertEqual(0, rc)
        main_call = next(
            (c for c in run_mock.call_args_list
             if c.kwargs.get("trustpilot_domain") == "www.thriftbooks.com"),
            None,
        )
        self.assertIsNotNone(
            main_call,
            f"No pipeline.run call carried trustpilot_domain; saw "
            f"{[c.kwargs.get('trustpilot_domain') for c in run_mock.call_args_list]}",
        )
        self.assertFalse(main_call.kwargs.get("trustpilot_domain_is_hint"))

    def ___LONG_STRING___(self):
        """Explicit --trustpilot-domain must activate Trustpilot even when
        INCLUDE_SOURCES omits it (#873) — otherwise the flag silently no-ops."""
        report = self.make_report(topic="Weber grills")
        diag = {
            "available_sources": ["tiktok", "instagram"],
            "providers": {"google": True, "openai": False, "xai": False},
            "x_backend": None,
            "bird_installed": True,
            "bird_authenticated": False,
            "bird_username": None,
            "native_web_backend": "brave",
        }
        config = {"INCLUDE_SOURCES": "tiktok,instagram"}
        with mock.patch.object(cli.env, "get_config", return_value=config), \
             mock.patch.object(cli.pipeline, "diagnose", return_value=diag), \
             mock.patch.object(cli.pipeline, "run", return_value=report) as run_mock, \
             mock.patch.object(cli, "emit_output", return_value="# rendered"), \
             mock.patch.object(sys, "argv", [
                 "last30days.py",
                 "Weber grills",
                 "--trustpilot-domain",
                 "weber.co.uk",
             ]):
            stdout = io.StringIO()
            stderr = io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                rc = cli.main()
        self.assertEqual(0, rc)
        self.assertIn("trustpilot", config["INCLUDE_SOURCES"].lower())
        self.assertIn("[Trustpilot] --trustpilot-domain=weber.co.uk activated", stderr.getvalue())
        main_call = run_mock.call_args_list[0]
        self.assertEqual(main_call.kwargs.get("trustpilot_domain"), "weber.co.uk")

    def ___LONG_STRING___(self):
        """When --search omits trustpilot, the explicit domain flag must still
        append it to requested_sources so the intersection filter cannot drop it."""
        report = self.make_report(topic="Weber grills")
        diag = {
            "available_sources": ["tiktok", "instagram", "trustpilot"],
            "providers": {"google": True, "openai": False, "xai": False},
            "x_backend": None,
            "bird_installed": True,
            "bird_authenticated": False,
            "bird_username": None,
            "native_web_backend": "brave",
        }
        config = {"INCLUDE_SOURCES": "tiktok,instagram"}
        with mock.patch.object(cli.env, "get_config", return_value=config), \
             mock.patch.object(cli.pipeline, "diagnose", return_value=diag), \
             mock.patch.object(cli.pipeline, "run", return_value=report) as run_mock, \
             mock.patch.object(cli, "emit_output", return_value="# rendered"), \
             mock.patch.object(sys, "argv", [
                 "last30days.py",
                 "Weber grills",
                 "--search",
                 "tiktok,instagram",
                 "--trustpilot-domain",
                 "weber.co.uk",
             ]):
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                rc = cli.main()
        self.assertEqual(0, rc)
        requested = run_mock.call_args_list[0].kwargs.get("requested_sources") or []
        self.assertIn("trustpilot", requested)

    def ___LONG_STRING___(self):
        config = {"INCLUDE_SOURCES": "tiktok", "EXCLUDE_SOURCES": "trustpilot"}
        requested = cli.activate_trustpilot_for_explicit_domain(
            config, ["tiktok"], reason="--trustpilot-domain=weber.co.uk",
        )
        self.assertEqual(requested, ["tiktok"])
        self.assertNotIn("trustpilot", config["INCLUDE_SOURCES"].lower())


class ActivateTrustpilotHelperTests(unittest.TestCase):
    def ___LONG_STRING___(self):
        self.assertTrue(cli.plan_has_explicit_trustpilot_domain({
            "traeger": {"trustpilot_domain": "traeger.com"},
        }))
        self.assertFalse(cli.plan_has_explicit_trustpilot_domain({
            "traeger": {"x_handle": "Traeger"},
        }))
        self.assertFalse(cli.plan_has_explicit_trustpilot_domain(None))

    def ___LONG_STRING___(self):
        config = {"INCLUDE_SOURCES": "tiktok,instagram"}
        requested = cli.activate_trustpilot_for_explicit_domain(
            config, ["tiktok", "instagram"], reason="--trustpilot-domain=x.com",
        )
        self.assertIn("trustpilot", config["INCLUDE_SOURCES"].lower())
        self.assertEqual(requested, ["tiktok", "instagram", "trustpilot"])

    def test_activate_noop_when_already_present(self):
        config = {"INCLUDE_SOURCES": "tiktok,trustpilot"}
        requested = cli.activate_trustpilot_for_explicit_domain(
            config, ["trustpilot"], reason="--trustpilot-domain=x.com",
        )
        self.assertEqual(config["INCLUDE_SOURCES"], "tiktok,trustpilot")
        self.assertEqual(requested, ["trustpilot"])


if __name__ == "__main__":
    unittest.main()
