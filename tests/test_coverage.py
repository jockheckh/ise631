from scripts.audit_coverage import audit

def test_instructor_requirement_matrix_structure():
    assert audit() == []
