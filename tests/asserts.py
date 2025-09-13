from xml.dom import minidom


def verify_test_case(
    test_case_element: minidom.Element,
    expected_attributes: dict[str, str],
    error_message: str | None = None,
    error_output: str | None = None,
    error_type: str | None = None,
    failure_message: str | None = None,
    failure_output: str | None = None,
    failure_type: str | None = None,
    skipped_message: str | None = None,
    skipped_output: str | None = None,
    stdout: str | None = None,
    stderr: str | None = None,
    errors: list[dict[str, str | None]] | None = None,
    failures: list[dict[str, str | None]] | None = None,
    skipped: list[dict[str, str | None]] | None = None,
) -> None:
    for k, v in expected_attributes.items():
        assert test_case_element.attributes[k].value == v

    for k in test_case_element.attributes.keys():
        assert k in expected_attributes

        if stderr:
            first_child = test_case_element.getElementsByTagName("system-err")[
                0
            ].firstChild
            assert first_child is not None
            node_value = first_child.nodeValue
            assert node_value is not None
            assert node_value.strip() == stderr
        if stdout:
            first_child = test_case_element.getElementsByTagName("system-out")[
                0
            ].firstChild
            assert first_child is not None
            node_value = first_child.nodeValue
            assert node_value is not None
            assert node_value.strip() == stdout

        _errors = test_case_element.getElementsByTagName("error")
        if error_message or error_output:
            assert len(_errors) > 0
        elif errors:
            assert len(errors) == len(_errors)
        else:
            assert len(_errors) == 0

        if error_message:
            assert _errors[0].attributes["message"].value == error_message

        if error_type and _errors:
            assert _errors[0].attributes["type"].value == error_type

        if error_output:
            first_child = _errors[0].firstChild
            assert first_child is not None
            node_value = first_child.nodeValue
            assert node_value is not None
            assert node_value.strip() == error_output

        for error_exp, error_r in zip(errors or [], _errors, strict=False):
            assert error_r.attributes["message"].value == error_exp["message"]
            first_child = error_r.firstChild
            assert first_child is not None
            node_value = first_child.nodeValue
            assert node_value is not None
            assert node_value.strip() == error_exp["output"]
            assert error_r.attributes["type"].value == error_exp["type"]

        _failures = test_case_element.getElementsByTagName("failure")
        if failure_message or failure_output:
            assert len(_failures) > 0
        elif failures:
            assert len(failures) == len(_failures)
        else:
            assert len(_failures) == 0

        if failure_message:
            assert _failures[0].attributes["message"].value == failure_message

        if failure_type and _failures:
            assert _failures[0].attributes["type"].value == failure_type

        if failure_output:
            first_child = _failures[0].firstChild
            assert first_child is not None
            node_value = first_child.nodeValue
            assert node_value is not None
            assert node_value.strip() == failure_output

        for failure_exp, failure_r in zip(failures or [], _failures, strict=False):
            assert failure_r.attributes["message"].value == failure_exp["message"]
            first_child = failure_r.firstChild
            assert first_child is not None
            node_value = first_child.nodeValue
            assert node_value is not None
            assert node_value.strip() == failure_exp["output"]
            assert failure_r.attributes["type"].value == failure_exp["type"]

        _skipped = test_case_element.getElementsByTagName("skipped")
        if skipped_message or skipped_output:
            assert len(_skipped) > 0
        elif skipped:
            assert len(skipped) == len(_skipped)
        else:
            assert len(_skipped) == 0

        for skipped_exp, skipped_r in zip(skipped or [], _skipped, strict=False):
            assert skipped_r.attributes["message"].value == skipped_exp["message"]
            first_child = skipped_r.firstChild
            assert first_child is not None
            node_value = first_child.nodeValue
            assert node_value is not None
            assert node_value.strip() == skipped_exp["output"]
