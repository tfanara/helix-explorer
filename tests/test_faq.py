from dna.faq import FAQ, CATEGORIES, search_faq


def test_faq_has_basics_and_safety():
    assert len(FAQ) >= 25
    questions = {question for _, question, _ in FAQ}
    assert 'What is an allele?' in questions
    assert 'Does this app diagnose genetic diseases?' in questions
    assert 'Where does my uploaded DNA go?' in questions


def test_faq_search_and_categories():
    assert any('allele' in question.lower() for _, question, _ in search_faq(query='allele'))
    assert all(topic == 'DNA basics' for topic, _, _ in search_faq('DNA basics'))
    assert search_faq(query='notarealgeneticterm987') == []
    assert len(CATEGORIES) >= 3


def test_faq_unique_questions():
    questions = [question for _, question, _ in FAQ]
    assert len(questions) == len(set(questions))
