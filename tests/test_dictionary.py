import json
import pytest

from dictionary.main import Dictionary, InfoType, SearchMode
from dictionary.file_ops import NotADictionaryError, read_json, time, date_time
from datetime import date as date_
from pathlib import Path

file = Path("dict-test.json")
if file.exists():
    file.unlink()

test_dict = Dictionary("dict-test.json", "title", "author", "description")



with open('dict-test2.json', 'w') as f:
    json.dump({
        'title': 'title',
        'author': 'author',
        'description': 'description',
        'revision_date': str(date_.today()),
        'contents': {
            'keyword1': {
                'definitions': ['definition1'],
                'references': ['reference1']
            }
    }}, f)

with open('dict-test3.json', 'w') as f:
    json.dump({
        'key1': 'value1'
    }, f)


def test_new():
    assert test_dict.title == "title"
    assert test_dict.author == "author"
    assert test_dict.description == "description"
    assert test_dict.path == "dict-test.json"
    assert not test_dict.edited

    # This might be a problem, although it's a very small
    assert test_dict.revision_date == str(date_.today())


def test_add():
    test_dict.add("keyword1", "definition1", "reference1")
    assert test_dict == {
        "keyword1": {
            "definitions": ["definition1"],
            "references": ["reference1"]
        }
    }

    test_dict.add("keyword1", "definition2")
    assert test_dict == {
        "keyword1": {
            "definitions": ["definition1", "definition2"],
            "references": ["reference1"],
        }
    }

    test_dict.add("keyword1", "", "reference2")
    assert test_dict == {
        "keyword1": {
            "definitions": ["definition1", "definition2"],
            "references": ["reference1", "reference2"],
        }
    }

    with pytest.raises(ValueError):
        test_dict.add('new')


def test_save():
    test_dict.save()
    assert file.exists()
    with open("dict-test.json") as f:
        assert test_dict._convert_to_dict() == json.load(f)


def test_search():
    for i in ("keyword", "keywords", "keyswords", "keywords1", "keyswords1"):
        test_dict.add(i, "definition1", "reference1")

    assert test_dict.search("keyword") == [
        ("keyword", 0),
        ("keyword1", 1),
        ("keywords", 1),
        ("keyswords", 2),
        ("keywords1", 2),
    ]

    assert test_dict.search("keyword", mode=SearchMode.SubStr) == [
        ("keyword", 0),
        ("keyword1", 1),
        ("keywords", 1),
        ("keywords1", 2),
    ]

    assert test_dict.search("keyword", mode=SearchMode.Exact) == [
        ("keyword", 0)
    ]

    with pytest.raises(ValueError):
        test_dict.search("keyword", max_results=0)

    new_dict = Dictionary('temp.json', 'title', 'author', 'description')
    assert new_dict.search('keyword') is None


def test_information_on():
    assert test_dict.information_on("keyword", InfoType.Definitions) == [
        "definition1"
    ]
    assert test_dict.information_on("keyword1", InfoType.References) == [
        "reference1",
        "reference2",
    ]
    assert test_dict.information_on(
        'nonexistent', InfoType.Definitions
    ) is None


def test_remove():
    test_dict.remove("keyword1", "definition1", "reference1")
    assert test_dict["keyword1"] == {
        "definitions": ["definition2"],
        "references": ["reference2"],
    }

    test_dict.remove("keyword1", "definition2", "reference2")
    assert test_dict["keyword1"] == {
        "definitions": [],
        "references": [],
    }

    test_dict.remove("keyword")
    assert "keyword" not in test_dict

    with pytest.raises(ValueError):
        test_dict.remove('nonexistent')

    test_dict.add('nonexistent', 'definition', 'reference')
    with pytest.raises(ValueError):
        test_dict.remove('nonexistent', 'def')

    with pytest.raises(ValueError):
        test_dict.remove('nonexistent', '', 'ref')
        


def test_overrides():
    with pytest.raises(NotImplementedError):
        del test_dict['keywords']

    with pytest.raises(NotImplementedError):
        test_dict.clear()

    with pytest.raises(NotImplementedError):
        test_dict.popitem()

    with pytest.raises(NotImplementedError):
        test_dict.pop('keywords')

    with pytest.raises(NotImplementedError):
        test_dict[1] = []

    with pytest.raises(NotImplementedError):
        # VALID_KEYS = ("definitions", "references")
        # logging.error(all(key in VALID_KEYS for key in []))
        # logging.error(all(key in [] for key in VALID_KEYS))
        # logging.error('keyword' in test_dict)
        test_dict['keyword'] = []

    with pytest.raises(NotImplementedError):
        test_dict['keywords'] = []

def test_file_validation():
    assert read_json('dict-test2.json') == {
        'title': 'title',
        'author': 'author',
        'description': 'description',
        'revision_date': str(date_.today()),
        'contents': {
            'keyword1': {
                'definitions': ['definition1'],
                'references': ['reference1']
            }
    }}

    with pytest.raises(NotADictionaryError):
        read_json('dict-test3.json')

    with pytest.raises(FileNotFoundError):
        read_json('non-existent-file.json')

    with pytest.raises(FileNotFoundError):
        Dictionary('src/')

    assert Dictionary('dict-test2.json')

    # For the sake of code coverage
    assert time()
    assert date_time()
