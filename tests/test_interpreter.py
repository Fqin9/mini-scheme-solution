"""Behavioral checks for the public mini-Scheme command line interface."""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / "src" / "main.py"


def run_scheme(program, *files):
    return subprocess.run(
        [sys.executable, str(MAIN), *map(str, files)],
        input=program,
        text=True,
        capture_output=True,
        cwd=ROOT,
        check=False,
    )


class InterpreterTests(unittest.TestCase):
    def assert_program(self, program, expected):
        result = run_scheme(program)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, expected)

    def test_reader_comments_quotes_and_escaped_strings(self):
        self.assert_program("; ignore\n'a\n'(1 (2 3))\n\"a\\n\\t\\\"\\\\b\"", "a\n(1 (2 3))\n\"a\\n\\t\\\"\\\\b\"\n")

    def test_arithmetic_comparison_and_boolean_rules(self):
        self.assert_program(
            "(+ ) (* ) (- 5) (/ 7 2) (/ -7 2) (/ 2) "
            "(modulo 17 5) (quotient -7 2) (expt 2 3) "
            "(< 1 2 3) (= 'a 'a) (not 0) (and) (or) "
            "(and #f (/ 1 0)) (or 0 (/ 1 0))",
            "0\n1\n-5\n3\n-3\n0.5\n2\n-3\n8\n#t\n#t\n#f\n#t\n#f\n#f\n0\n",
        )

    def test_special_forms_and_lexical_scope(self):
        self.assert_program(
            "(define x 10) (define (f n) (if (= n 0) x (f (- n 1)))) "
            "(let ((x 3) (y x)) (list x y)) "
            "(define addx (let ((x 7)) (lambda (n) (+ x n)))) "
            "(addx 5) (f 3) "
            "(cond ((= 1 2) 'no) ((= 2 2)) (else 'bad)) "
            "(begin (define z 2) (+ z 3)) (if #f 1)",
            "x\nf\n(3 10)\naddx\n12\n10\n#t\n5\n",
        )

    def test_pairs_lists_and_equality(self):
        self.assert_program(
            "(cons 1 2) (cons 1 '(2 3)) (car '(4 5)) (cdr '(4 5)) "
            "(length '(a b c)) (append '(1 2) '(3 4)) "
            "(null? '()) (pair? '(1)) (list? (cons 1 2)) "
            "(eq? '(1) '(1)) (equal? '(1) (list 1)) "
            "(eq? '() '()) (equal? #t 1) (equal? 'a \"a\")",
            "(1 . 2)\n(1 2 3)\n4\n(5)\n3\n(1 2 3 4)\n#t\n#t\n#f\n#f\n#t\n#t\n#f\n#f\n",
        )

    def test_equal_handles_long_lists_and_tail_mismatches(self):
        self.assert_program(
            "(begin (define xs '(1)) "
            + "(define xs (append xs xs)) " * 10
            + "(list (length xs) (equal? xs xs) "
            "(equal? xs (append xs '())) "
            "(equal? xs (append (cdr xs) '(2))) "
            "(equal? xs (append xs '(1)))))",
            "(1024 #t #t #f #f)\n",
        )

    def test_equal_handles_deeply_nested_pairs(self):
        self.assert_program(
            "(begin (define xs (cons 'a 'b)) "
            "(define ys (cons 'a 'b)) (define zs (cons 'a 'c)) "
            + "(define xs (list xs)) (define ys (list ys)) "
            "(define zs (list zs)) " * 1200
            + "(list (equal? xs ys) (equal? xs zs)))",
            "(#t #f)\n",
        )

    def test_quoted_dot_is_distinct_from_a_string_dot(self):
        self.assert_program(
            "'(1 . 2) '(1 \".\" 2) (list? '(1 . 2))",
            "(1 . 2)\n(1 \".\" 2)\n#f\n",
        )

    def test_predicates_and_output(self):
        self.assert_program(
            "(number? 3) (boolean? #t) (symbol? 'x) (string? \"x\") "
            "(procedure? car) (zero? 0) (even? 4) (odd? 5) "
            "(display \"hi\") (display 2) (newline) \"a\\nb\"",
            "#t\n#t\n#t\n#t\n#t\n#t\n#t\n#t\nhi2\n\"a\\nb\"\n",
        )

    def test_files_share_one_environment(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            first = Path(directory) / "first.scm"
            second = Path(directory) / "second.scm"
            first.write_text("(define x 4)", encoding="utf-8")
            second.write_text("(+ x 5)", encoding="utf-8")
            result = run_scheme(None, first, second)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, "x\n9\n")


if __name__ == "__main__":
    unittest.main()
