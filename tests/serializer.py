import codecs
import os
import tempfile
from xml.dom import minicompat, minidom

from junit_xml import TestSuite, to_xml_report_file, to_xml_report_string


def serialize_and_read(
    test_suites: TestSuite | list[TestSuite],
    to_file: bool = False,
    prettyprint: bool = False,
    encoding: str | None = None,
) -> list[tuple[minidom.Element, minicompat.NodeList[minidom.Element]]]:
    """
    Write the test suite to an XML string and then re-reads it using minidom.

    Return => (test suite element, list of test case elements).
    """
    if not isinstance(test_suites, list):
        test_suites = [test_suites]

    if to_file:
        fd, filename = tempfile.mkstemp(text=True)
        os.close(fd)
        with codecs.open(filename, mode="w", encoding=encoding) as f:
            to_xml_report_file(
                f, test_suites, prettyprint=prettyprint, encoding=encoding
            )
        print(f"Serialized XML to temp file [{filename}]")
        xmldoc = minidom.parse(filename)
        os.remove(filename)
    else:
        xml_string = to_xml_report_string(
            test_suites, prettyprint=prettyprint, encoding=encoding
        )
        print(f"Serialized XML to string:\n{xml_string}")
        if encoding:
            xml_string = xml_string.encode(encoding)
        xmldoc = minidom.parseString(xml_string)

    def remove_blanks(node: minidom.Document | minidom.Element) -> None:
        for x in node.childNodes:
            if x.nodeType == minidom.Node.TEXT_NODE:
                if x.nodeValue:
                    x.nodeValue = x.nodeValue.strip()
            elif x.nodeType == minidom.Node.ELEMENT_NODE:
                remove_blanks(x)

    remove_blanks(xmldoc)
    xmldoc.normalize()

    ret: list[tuple[minidom.Element, minicompat.NodeList[minidom.Element]]] = []
    suites = xmldoc.getElementsByTagName("testsuites")[0]
    for suite in suites.getElementsByTagName("testsuite"):
        cases = suite.getElementsByTagName("testcase")
        ret.append((suite, cases))
    return ret
