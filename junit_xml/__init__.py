import re
import sys
import warnings
import xml.dom.minidom
import xml.etree.ElementTree as ET
from collections import defaultdict
from typing import TextIO

"""
Based on the understanding of what Jenkins can parse for JUnit XML files.

<?xml version="1.0" encoding="utf-8"?>
<testsuites errors="1" failures="1" tests="4" time="45">
    <testsuite errors="1" failures="1" hostname="localhost" id="0" name="test1"
               package="testdb" tests="4" timestamp="2012-11-15T01:02:29">
        <properties>
            <property name="assert-passed" value="1"/>
        </properties>
        <testcase classname="testdb.directory" name="1-passed-test" time="10"/>
        <testcase classname="testdb.directory" name="2-failed-test" time="20">
            <failure message="Assertion FAILED: failed assert" type="failure">
                the output of the testcase
            </failure>
        </testcase>
        <testcase classname="package.directory" name="3-errord-test" time="15">
            <error message="Assertion ERROR: error assert" type="error">
                the output of the testcase
            </error>
        </testcase>
        <testcase classname="package.directory" name="3-skipped-test" time="0">
            <skipped message="SKIPPED Test" type="skipped">
                the output of the testcase
            </skipped>
        </testcase>
        <testcase classname="testdb.directory" name="3-passed-test" time="10">
            <system-out>
                I am system output
            </system-out>
            <system-err>
                I am the error output
            </system-err>
        </testcase>
    </testsuite>
</testsuites>
"""


def decode(var: str | bytes | int) -> str:
    """If not already unicode, decode it."""
    return str(var)


class TestSuite:
    """
    Suite of test cases.

    Can handle unicode strings or binary strings if their encoding is provided.
    """

    def __init__(
        self,
        name: str,
        test_cases: "list[TestCase] | None" = None,
        hostname: str | None = None,
        id: int | str | None = None,  # noqa: A002
        package: str | None = None,
        timestamp: int | None = None,
        properties: dict[str, str] | None = None,
        file: str | None = None,
        log: str | None = None,
        url: str | None = None,
        stdout: str | None = None,
        stderr: str | None = None,
    ) -> None:
        self.name = name
        if not test_cases:
            test_cases = []
        try:
            iter(test_cases)
        except TypeError as e:
            error_message = "test_cases must be a list of test cases"
            raise TypeError(error_message) from e
        self.test_cases = test_cases
        self.timestamp = timestamp
        self.hostname = hostname
        self.id = id
        self.package = package
        self.file = file
        self.log = log
        self.url = url
        self.stdout = stdout
        self.stderr = stderr
        self.properties = properties

    def build_xml_doc(self) -> ET.Element:
        """
        Build the XML document for the JUnit test suite.

        Produces clean unicode strings and decodes non-unicode
        with the help of encoding.
        @param encoding: Used to decode encoded strings.
        @return: XML document with unicode string elements
        """
        # build the test suite element
        test_suite_attributes: dict[str, str] = {}
        if any(c.assertions for c in self.test_cases):
            test_suite_attributes["assertions"] = str(
                sum([int(c.assertions) for c in self.test_cases if c.assertions])
            )
        test_suite_attributes["disabled"] = str(
            len([c for c in self.test_cases if not c.is_enabled])
        )
        test_suite_attributes["errors"] = str(
            len([c for c in self.test_cases if c.is_error()])
        )
        test_suite_attributes["failures"] = str(
            len([c for c in self.test_cases if c.is_failure()])
        )
        test_suite_attributes["name"] = decode(self.name)
        test_suite_attributes["skipped"] = str(
            len([c for c in self.test_cases if c.is_skipped()])
        )
        test_suite_attributes["tests"] = str(len(self.test_cases))
        test_suite_attributes["time"] = str(
            sum(c.elapsed_sec for c in self.test_cases if c.elapsed_sec)
        )

        if self.hostname:
            test_suite_attributes["hostname"] = decode(self.hostname)
        if self.id:
            test_suite_attributes["id"] = decode(self.id)
        if self.package:
            test_suite_attributes["package"] = decode(self.package)
        if self.timestamp:
            test_suite_attributes["timestamp"] = decode(self.timestamp)
        if self.file:
            test_suite_attributes["file"] = decode(self.file)
        if self.log:
            test_suite_attributes["log"] = decode(self.log)
        if self.url:
            test_suite_attributes["url"] = decode(self.url)

        xml_element = ET.Element("testsuite", test_suite_attributes)

        # add any properties
        if self.properties:
            props_element = ET.SubElement(xml_element, "properties")
            for k, v in self.properties.items():
                attrs = {"name": decode(k), "value": decode(v)}
                ET.SubElement(props_element, "property", attrs)

        # add test suite stdout
        if self.stdout:
            stdout_element = ET.SubElement(xml_element, "system-out")
            stdout_element.text = decode(self.stdout)

        # add test suite stderr
        if self.stderr:
            stderr_element = ET.SubElement(xml_element, "system-err")
            stderr_element.text = decode(self.stderr)

        # test cases
        for case in self.test_cases:
            test_case_attributes: dict[str, str] = {}
            test_case_attributes["name"] = decode(case.name)
            if case.assertions:
                # Number of assertions in the test case
                test_case_attributes["assertions"] = f"{case.assertions:d}"
            if case.elapsed_sec:
                test_case_attributes["time"] = f"{case.elapsed_sec:f}"
            if case.timestamp:
                test_case_attributes["timestamp"] = decode(case.timestamp)
            if case.classname:
                test_case_attributes["classname"] = decode(case.classname)
            if case.status:
                test_case_attributes["status"] = decode(case.status)
            if case.category:
                test_case_attributes["class"] = decode(case.category)
            if case.file:
                test_case_attributes["file"] = decode(case.file)
            if case.line:
                test_case_attributes["line"] = decode(case.line)
            if case.log:
                test_case_attributes["log"] = decode(case.log)
            if case.url:
                test_case_attributes["url"] = decode(case.url)

            test_case_element = ET.SubElement(
                xml_element, "testcase", test_case_attributes
            )

            # failures
            for failure in case.failures:
                if failure["output"] or failure["message"]:
                    attrs = {"type": "failure"}
                    if failure["message"]:
                        attrs["message"] = decode(failure["message"])
                    if failure["type"]:
                        attrs["type"] = decode(failure["type"])
                    failure_element = ET.Element("failure", attrs)
                    if failure["output"]:
                        failure_element.text = decode(failure["output"])
                    test_case_element.append(failure_element)

            # errors
            for error in case.errors:
                if error["message"] or error["output"]:
                    attrs = {"type": "error"}
                    if error["message"]:
                        attrs["message"] = decode(error["message"])
                    if error["type"]:
                        attrs["type"] = decode(error["type"])
                    error_element = ET.Element("error", attrs)
                    if error["output"]:
                        error_element.text = decode(error["output"])
                    test_case_element.append(error_element)

            # skippeds
            for skipped in case.skipped:
                attrs = {"type": "skipped"}
                if skipped["message"]:
                    attrs["message"] = decode(skipped["message"])
                skipped_element = ET.Element("skipped", attrs)
                if skipped["output"]:
                    skipped_element.text = decode(skipped["output"])
                test_case_element.append(skipped_element)

            # test stdout
            if case.stdout:
                stdout_element = ET.Element("system-out")
                stdout_element.text = decode(case.stdout)
                test_case_element.append(stdout_element)

            # test stderr
            if case.stderr:
                stderr_element = ET.Element("system-err")
                stderr_element.text = decode(case.stderr)
                test_case_element.append(stderr_element)

        return xml_element

    @staticmethod
    def to_xml_string(
        test_suites: "list[TestSuite]",
        prettyprint: bool = True,
        encoding: str | None = None,
    ) -> str:
        """
        Return the string representation of the JUnit XML document.

        @param encoding: The encoding of the input.
        @return: unicode string
        """
        warnings.warn(
            "Testsuite.to_xml_string is deprecated. "
            "It will be removed in version 2.0.0. "
            "Use function to_xml_report_string",
            DeprecationWarning,
        )
        return to_xml_report_string(test_suites, prettyprint, encoding)

    @staticmethod
    def to_file(
        file_descriptor: TextIO,
        test_suites: "list[TestSuite]",
        prettyprint: bool = True,
        encoding: str | None = None,
    ) -> None:
        """Write the JUnit XML document to a file."""
        warnings.warn(
            "Testsuite.to_file is deprecated. "
            "It will be removed in version 2.0.0. "
            "Use function to_xml_report_file",
            DeprecationWarning,
        )
        to_xml_report_file(file_descriptor, test_suites, prettyprint, encoding)


def to_xml_report_string(
    test_suites: list[TestSuite], prettyprint: bool = True, encoding: str | None = None
) -> str:
    """
    Return the string representation of the JUnit XML document.

    @param encoding: The encoding of the input.
    @return: unicode string
    """
    try:
        iter(test_suites)
    except TypeError as e:
        error_message = "test_suites must be a list of test suites"
        raise TypeError(error_message) from e

    xml_element = ET.Element("testsuites")
    attributes: dict[str, int | float] = defaultdict(int)
    for ts in test_suites:
        ts_xml = ts.build_xml_doc()
        for key in ["disabled", "errors", "failures", "tests"]:
            attributes[key] += int(ts_xml.get(key, 0))
        for key in ["time"]:
            attributes[key] += float(ts_xml.get(key, 0))
        xml_element.append(ts_xml)
    for key, value in attributes.items():
        xml_element.set(key, str(value))

    xml_string = ET.tostring(xml_element, encoding=encoding)
    # is encoded now
    xml_string = _clean_illegal_xml_chars(xml_string.decode(encoding or "utf-8"))
    # is unicode now

    if prettyprint:
        # minidom.parseString() works just on correctly encoded binary strings
        xml_string = xml_string.encode(encoding or "utf-8")
        xml_string = xml.dom.minidom.parseString(xml_string)
        # toprettyxml() produces unicode if no encoding is being passed
        # or binary string with an encoding
        xml_string = xml_string.toprettyxml(encoding=encoding)
        if not isinstance(xml_string, str):
            xml_string = xml_string.decode(encoding or "utf-8")
        # is unicode now
    return xml_string


def to_xml_report_file(
    file_descriptor: TextIO,
    test_suites: list[TestSuite],
    prettyprint: bool = True,
    encoding: str | None = None,
) -> None:
    """Write the JUnit XML document to a file."""
    xml_string = to_xml_report_string(
        test_suites, prettyprint=prettyprint, encoding=encoding
    )
    # has problems with encoded str with non-ASCII (non-default-encoding) characters!
    file_descriptor.write(xml_string)


def _clean_illegal_xml_chars(string_to_clean: str) -> str:
    """
    Remove any illegal unicode characters from the given XML string.

    @see: http://stackoverflow.com/questions/1707890/fast-way-to-filter-illegal-xml-unicode-chars-in-python
    """
    illegal_unichrs = [
        (0x00, 0x08),
        (0x0B, 0x1F),
        (0x7F, 0x84),
        (0x86, 0x9F),
        (0xD800, 0xDFFF),
        (0xFDD0, 0xFDDF),
        (0xFFFE, 0xFFFF),
        (0x1FFFE, 0x1FFFF),
        (0x2FFFE, 0x2FFFF),
        (0x3FFFE, 0x3FFFF),
        (0x4FFFE, 0x4FFFF),
        (0x5FFFE, 0x5FFFF),
        (0x6FFFE, 0x6FFFF),
        (0x7FFFE, 0x7FFFF),
        (0x8FFFE, 0x8FFFF),
        (0x9FFFE, 0x9FFFF),
        (0xAFFFE, 0xAFFFF),
        (0xBFFFE, 0xBFFFF),
        (0xCFFFE, 0xCFFFF),
        (0xDFFFE, 0xDFFFF),
        (0xEFFFE, 0xEFFFF),
        (0xFFFFE, 0xFFFFF),
        (0x10FFFE, 0x10FFFF),
    ]

    illegal_ranges = [
        f"{chr(low)}-{chr(high)}"
        for (low, high) in illegal_unichrs
        if low < sys.maxunicode
    ]

    illegal_xml_re = re.compile("[{}]".format("".join(illegal_ranges)))
    return illegal_xml_re.sub("", string_to_clean)


class TestCase:
    """A JUnit test case with a result and possibly some stdout or stderr."""

    def __init__(
        self,
        name: str,
        classname: str | None = None,
        elapsed_sec: float | None = None,
        stdout: str | None = None,
        stderr: str | None = None,
        assertions: int | None = None,
        timestamp: int | None = None,
        status: str | None = None,
        category: str | None = None,
        file: str | None = None,
        line: str | None = None,
        log: str | None = None,
        url: str | None = None,
        allow_multiple_subelements: bool = False,
    ) -> None:
        self.name = name
        self.assertions = assertions
        self.elapsed_sec = elapsed_sec
        self.timestamp = timestamp
        self.classname = classname
        self.status = status
        self.category = category
        self.file = file
        self.line = line
        self.log = log
        self.url = url
        self.stdout = stdout
        self.stderr = stderr

        self.is_enabled = True
        self.errors: list[dict[str, str | None]] = []
        self.failures: list[dict[str, str | None]] = []
        self.skipped: list[dict[str, str | None]] = []
        self.allow_multiple_subelements = allow_multiple_subelements

    def add_error_info(
        self,
        message: str | None = None,
        output: str | None = None,
        error_type: str | None = None,
    ) -> None:
        """Add an error message, output, or both to the test case."""
        error: dict[str, str | None] = {}
        error["message"] = message
        error["output"] = output
        error["type"] = error_type
        if self.allow_multiple_subelements:
            if message or output:
                self.errors.append(error)
        elif not len(self.errors):
            self.errors.append(error)
        else:
            if message:
                self.errors[0]["message"] = message
            if output:
                self.errors[0]["output"] = output
            if error_type:
                self.errors[0]["type"] = error_type

    def add_failure_info(
        self,
        message: str | None = None,
        output: str | None = None,
        failure_type: str | None = None,
    ) -> None:
        """Add a failure message, output, or both to the test case."""
        failure: dict[str, str | None] = {}
        failure["message"] = message
        failure["output"] = output
        failure["type"] = failure_type
        if self.allow_multiple_subelements:
            if message or output:
                self.failures.append(failure)
        elif not len(self.failures):
            self.failures.append(failure)
        else:
            if message:
                self.failures[0]["message"] = message
            if output:
                self.failures[0]["output"] = output
            if failure_type:
                self.failures[0]["type"] = failure_type

    def add_skipped_info(
        self, message: str | None = None, output: str | None = None
    ) -> None:
        """Add a skipped message, output, or both to the test case."""
        skipped: dict[str, str | None] = {}
        skipped["message"] = message
        skipped["output"] = output
        if self.allow_multiple_subelements:
            if message or output:
                self.skipped.append(skipped)
        elif not len(self.skipped):
            self.skipped.append(skipped)
        else:
            if message:
                self.skipped[0]["message"] = message
            if output:
                self.skipped[0]["output"] = output

    def is_failure(self) -> bool:
        """Return true if this test case is a failure."""
        return sum(1 for f in self.failures if f["message"] or f["output"]) > 0

    def is_error(self) -> bool:
        """Return true if this test case is an error."""
        return sum(1 for e in self.errors if e["message"] or e["output"]) > 0

    def is_skipped(self) -> bool:
        """Return true if this test case has been skipped."""
        return len(self.skipped) > 0


__all__ = ["TestCase", "TestSuite", "to_xml_report_file", "to_xml_report_string"]
