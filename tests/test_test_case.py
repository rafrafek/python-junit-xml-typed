from junit_xml import TestCase as Case
from junit_xml import TestSuite as Suite
from junit_xml import decode

from .asserts import verify_test_case
from .serializer import serialize_and_read


def test_init() -> None:
    _, tcs = serialize_and_read(Suite("test", [Case("Test1")]))[0]
    verify_test_case(tcs[0], {"name": "Test1"})


def test_init_classname() -> None:
    _, tcs = serialize_and_read(
        Suite("test", [Case(name="Test1", classname="some.class.name")])
    )[0]
    verify_test_case(tcs[0], {"name": "Test1", "classname": "some.class.name"})


def test_init_classname_time() -> None:
    _, tcs = serialize_and_read(
        Suite(
            "test",
            [Case(name="Test1", classname="some.class.name", elapsed_sec=123.345)],
        )
    )[0]
    verify_test_case(
        tcs[0],
        {"name": "Test1", "classname": "some.class.name", "time": (f"{123.345:f}")},
    )


def test_init_classname_time_timestamp() -> None:
    _, tcs = serialize_and_read(
        Suite(
            "test",
            [
                Case(
                    name="Test1",
                    classname="some.class.name",
                    elapsed_sec=123.345,
                    timestamp=99999,
                )
            ],
        )
    )[0]
    verify_test_case(
        tcs[0],
        {
            "name": "Test1",
            "classname": "some.class.name",
            "time": (f"{123.345:f}"),
            "timestamp": (f"{99999}"),
        },
    )


def test_init_stderr() -> None:
    _, tcs = serialize_and_read(
        Suite(
            "test",
            [
                Case(
                    name="Test1",
                    classname="some.class.name",
                    elapsed_sec=123.345,
                    stderr="I am stderr!",
                )
            ],
        )
    )[0]
    verify_test_case(
        tcs[0],
        {"name": "Test1", "classname": "some.class.name", "time": (f"{123.345:f}")},
        stderr="I am stderr!",
    )


def test_init_stdout_stderr() -> None:
    _, tcs = serialize_and_read(
        Suite(
            "test",
            [
                Case(
                    name="Test1",
                    classname="some.class.name",
                    elapsed_sec=123.345,
                    stdout="I am stdout!",
                    stderr="I am stderr!",
                )
            ],
        )
    )[0]
    verify_test_case(
        tcs[0],
        {"name": "Test1", "classname": "some.class.name", "time": (f"{123.345:f}")},
        stdout="I am stdout!",
        stderr="I am stderr!",
    )


def test_init_disable() -> None:
    tc = Case("Disabled-Test")
    tc.is_enabled = False
    _, tcs = serialize_and_read(Suite("test", [tc]))[0]
    verify_test_case(tcs[0], {"name": "Disabled-Test"})


def test_init_failure_message() -> None:
    tc = Case("Failure-Message")
    tc.add_failure_info("failure message")
    _, tcs = serialize_and_read(Suite("test", [tc]))[0]
    verify_test_case(
        tcs[0], {"name": "Failure-Message"}, failure_message="failure message"
    )


def test_init_failure_output() -> None:
    tc = Case("Failure-Output")
    tc.add_failure_info(output="I failed!")
    _, tcs = serialize_and_read(Suite("test", [tc]))[0]
    verify_test_case(tcs[0], {"name": "Failure-Output"}, failure_output="I failed!")


def test_init_failure_type() -> None:
    tc = Case("Failure-Type")
    tc.add_failure_info(failure_type="com.example.Error")
    _, tcs = serialize_and_read(Suite("test", [tc]))[0]
    verify_test_case(tcs[0], {"name": "Failure-Type"})

    tc.add_failure_info("failure message")
    _, tcs = serialize_and_read(Suite("test", [tc]))[0]
    verify_test_case(
        tcs[0],
        {"name": "Failure-Type"},
        failure_message="failure message",
        failure_type="com.example.Error",
    )


def test_init_failure() -> None:
    tc = Case("Failure-Message-and-Output")
    tc.add_failure_info("failure message", "I failed!")
    _, tcs = serialize_and_read(Suite("test", [tc]))[0]
    verify_test_case(
        tcs[0],
        {"name": "Failure-Message-and-Output"},
        failure_message="failure message",
        failure_output="I failed!",
        failure_type="failure",
    )


def test_init_error_message() -> None:
    tc = Case("Error-Message")
    tc.add_error_info("error message")
    _, tcs = serialize_and_read(Suite("test", [tc]))[0]
    verify_test_case(tcs[0], {"name": "Error-Message"}, error_message="error message")


def test_init_error_output() -> None:
    tc = Case("Error-Output")
    tc.add_error_info(output="I errored!")
    _, tcs = serialize_and_read(Suite("test", [tc]))[0]
    verify_test_case(tcs[0], {"name": "Error-Output"}, error_output="I errored!")


def test_init_error_type() -> None:
    tc = Case("Error-Type")
    tc.add_error_info(error_type="com.example.Error")
    _, tcs = serialize_and_read(Suite("test", [tc]))[0]
    verify_test_case(tcs[0], {"name": "Error-Type"})

    tc.add_error_info("error message")
    _, tcs = serialize_and_read(Suite("test", [tc]))[0]
    verify_test_case(
        tcs[0],
        {"name": "Error-Type"},
        error_message="error message",
        error_type="com.example.Error",
    )


def test_init_error() -> None:
    tc = Case("Error-Message-and-Output")
    tc.add_error_info("error message", "I errored!")
    _, tcs = serialize_and_read(Suite("test", [tc]))[0]
    verify_test_case(
        tcs[0],
        {"name": "Error-Message-and-Output"},
        error_message="error message",
        error_output="I errored!",
        error_type="error",
    )


def test_init_skipped_message() -> None:
    tc = Case("Skipped-Message")
    tc.add_skipped_info("skipped message")
    _, tcs = serialize_and_read(Suite("test", [tc]))[0]
    verify_test_case(
        tcs[0], {"name": "Skipped-Message"}, skipped_message="skipped message"
    )


def test_init_skipped_output() -> None:
    tc = Case("Skipped-Output")
    tc.add_skipped_info(output="I skipped!")
    _, tcs = serialize_and_read(Suite("test", [tc]))[0]
    verify_test_case(tcs[0], {"name": "Skipped-Output"}, skipped_output="I skipped!")


def test_init_skipped_err_output() -> None:
    tc = Case("Skipped-Output")
    tc.add_skipped_info(output="I skipped!")
    tc.add_error_info(output="I skipped with an error!")
    _, tcs = serialize_and_read(Suite("test", [tc]))[0]
    verify_test_case(
        tcs[0],
        {"name": "Skipped-Output"},
        skipped_output="I skipped!",
        error_output="I skipped with an error!",
    )


def test_init_skipped() -> None:
    tc = Case("Skipped-Message-and-Output")
    tc.add_skipped_info("skipped message", "I skipped!")
    _, tcs = serialize_and_read(Suite("test", [tc]))[0]
    verify_test_case(
        tcs[0],
        {"name": "Skipped-Message-and-Output"},
        skipped_message="skipped message",
        skipped_output="I skipped!",
    )


def test_init_legal_unicode_char() -> None:
    tc = Case("Failure-Message")
    tc.add_failure_info("failure message with legal unicode char: [\x22]")
    _, tcs = serialize_and_read(Suite("test", [tc]))[0]
    verify_test_case(
        tcs[0],
        {"name": "Failure-Message"},
        failure_message="failure message with legal unicode char: [\x22]",
    )


def test_init_illegal_unicode_char() -> None:
    tc = Case("Failure-Message")
    tc.add_failure_info("failure message with illegal unicode char: [\x02]")
    _, tcs = serialize_and_read(Suite("test", [tc]))[0]
    verify_test_case(
        tcs[0],
        {"name": "Failure-Message"},
        failure_message="failure message with illegal unicode char: []",
    )


def test_init_utf8() -> None:
    tc = Case(
        name="Test äöü",
        classname="some.class.name.äöü",
        elapsed_sec=123.345,
        stdout="I am stdöüt!",
        stderr="I am stdärr!",
    )
    tc.add_skipped_info(message="Skipped äöü", output="I skippäd!")
    tc.add_error_info(message="Skipped error äöü", output="I skippäd with an error!")
    test_suite = Suite("Test UTF-8", [tc])
    _, tcs = serialize_and_read(test_suite, encoding="utf-8")[0]
    verify_test_case(
        tcs[0],
        {
            "name": decode("Test äöü"),
            "classname": decode("some.class.name.äöü"),
            "time": (f"{123.345:f}"),
        },
        stdout=decode("I am stdöüt!"),
        stderr=decode("I am stdärr!"),
        skipped_message=decode("Skipped äöü"),
        skipped_output=decode("I skippäd!"),
        error_message=decode("Skipped error äöü"),
        error_output=decode("I skippäd with an error!"),
    )


def test_init_unicode() -> None:
    tc = Case(
        name=decode("Test äöü"),
        classname=decode("some.class.name.äöü"),
        elapsed_sec=123.345,
        stdout=decode("I am stdöüt!"),
        stderr=decode("I am stdärr!"),
    )
    tc.add_skipped_info(message=decode("Skipped äöü"), output=decode("I skippäd!"))
    tc.add_error_info(
        message=decode("Skipped error äöü"), output=decode("I skippäd with an error!")
    )

    _, tcs = serialize_and_read(Suite("Test Unicode", [tc]))[0]
    verify_test_case(
        tcs[0],
        {
            "name": decode("Test äöü"),
            "classname": decode("some.class.name.äöü"),
            "time": (f"{123.345:f}"),
        },
        stdout=decode("I am stdöüt!"),
        stderr=decode("I am stdärr!"),
        skipped_message=decode("Skipped äöü"),
        skipped_output=decode("I skippäd!"),
        error_message=decode("Skipped error äöü"),
        error_output=decode("I skippäd with an error!"),
    )


def test_multiple_errors() -> None:
    """Test multiple errors in one test case."""
    tc = Case("Multiple error", allow_multiple_subelements=True)
    tc.add_error_info("First error", "First error message")
    (_, tcs) = serialize_and_read(Suite("test", [tc]))[0]
    verify_test_case(
        tcs[0],
        {"name": "Multiple error"},
        errors=[
            {"message": "First error", "output": "First error message", "type": "error"}
        ],
    )
    tc.add_error_info("Second error", "Second error message")
    (_, tcs) = serialize_and_read(Suite("test", [tc]))[0]
    verify_test_case(
        tcs[0],
        {"name": "Multiple error"},
        errors=[
            {
                "message": "First error",
                "output": "First error message",
                "type": "error",
            },
            {
                "message": "Second error",
                "output": "Second error message",
                "type": "error",
            },
        ],
    )


def test_multiple_failures() -> None:
    """Test multiple failures in one test case."""
    tc = Case("Multiple failures", allow_multiple_subelements=True)
    tc.add_failure_info("First failure", "First failure message")
    (_, tcs) = serialize_and_read(Suite("test", [tc]))[0]
    verify_test_case(
        tcs[0],
        {"name": "Multiple failures"},
        failures=[
            {
                "message": "First failure",
                "output": "First failure message",
                "type": "failure",
            }
        ],
    )
    tc.add_failure_info("Second failure", "Second failure message")
    (_, tcs) = serialize_and_read(Suite("test", [tc]))[0]
    verify_test_case(
        tcs[0],
        {"name": "Multiple failures"},
        failures=[
            {
                "message": "First failure",
                "output": "First failure message",
                "type": "failure",
            },
            {
                "message": "Second failure",
                "output": "Second failure message",
                "type": "failure",
            },
        ],
    )


def test_multiple_skipped() -> None:
    """Test multiple skipped messages in one test case."""
    tc = Case("Multiple skipped", allow_multiple_subelements=True)
    tc.add_skipped_info("First skipped", "First skipped message")
    (_, tcs) = serialize_and_read(Suite("test", [tc]))[0]
    verify_test_case(
        tcs[0],
        {"name": "Multiple skipped"},
        skipped=[{"message": "First skipped", "output": "First skipped message"}],
    )
    tc.add_skipped_info("Second skipped", "Second skipped message")
    (_, tcs) = serialize_and_read(Suite("test", [tc]))[0]
    verify_test_case(
        tcs[0],
        {"name": "Multiple skipped"},
        skipped=[
            {"message": "First skipped", "output": "First skipped message"},
            {"message": "Second skipped", "output": "Second skipped message"},
        ],
    )
