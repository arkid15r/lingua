# coding=utf-8
import mock
import pytest
import io
from lingua.extractors.python import PythonExtractor


python_extractor = PythonExtractor()
source = None


@pytest.fixture
def fake_source(request):
    patcher = mock.patch('lingua.extractors.python._open',
            side_effect=lambda *a: io.StringIO(source))
    patcher.start()
    request.addfinalizer(patcher.stop)


@pytest.mark.usefixtures('fake_source')
def test_syntax_error():
    global source
    options = mock.Mock()
    options.keywords = []
    source = u'''def class xya _(u'føo' 1)'''
    with pytest.raises(SystemExit):
        generator = python_extractor('filename', options)
        list(generator)


@pytest.mark.usefixtures('fake_source')
def test_multiline_string():
    global source
    options = mock.Mock()
    options.keywords = []
    source = u'''_(u'őne two '\n'three')'''
    messages = list(python_extractor('filename', options))
    assert len(messages) == 1
    assert messages[0].msgid == u'őne two three'


@pytest.mark.usefixtures('fake_source')
def test_plural():
    global source
    options = mock.Mock()
    options.keywords = []
    source = u'''ngettext(u'one côw', u'%d cows', 5)'''
    messages = list(python_extractor('filename', options))
    assert len(messages) == 1
    assert messages[0].msgid == u'one côw'
    assert messages[0].msgid_plural == u'%d cows'


@pytest.mark.usefixtures('fake_source')
def test_translationstring_parameters():
    global source
    options = mock.Mock()
    options.keywords = []
    source = u'''_(u'msgid', default=u'Canonical text')'''
    messages = list(python_extractor('filename', options))
    assert len(messages) == 1
    assert messages[0].msgctxt is None
    assert messages[0].msgid == u'msgid'
    assert messages[0].comment == u'Default: Canonical text'


@pytest.mark.usefixtures('fake_source')
def test_translationstring_context():
    global source
    options = mock.Mock()
    options.keywords = []
    source = u'''_(u'Canonical text', context='button')'''
    messages = list(python_extractor('filename', options))
    assert len(messages) == 1
    assert messages[0].msgctxt == 'button'
    assert messages[0].msgid == u'Canonical text'


@pytest.mark.usefixtures('fake_source')
def test_function_call_in_keyword():
    global source
    options = mock.Mock()
    options.keywords = ['other']
    source = u'''other(six.u('word'))'''
    messages = list(python_extractor('filename', options))
    assert len(messages) == 0


@pytest.mark.usefixtures('fake_source')
def test_use_lineno_parameter():
    global source
    options = mock.Mock()
    options.keywords = []
    source = u'''_(u'word')'''
    messages = list(python_extractor('filename', options, lineno=5))
    assert len(messages) == 1
    assert messages[0].location[1] == 6


@pytest.mark.usefixtures('fake_source')
def test_skip_comments():
    global source
    options = mock.Mock()
    options.comment_tag = None
    source = u'''# source comment\n_(u'word')'''
    messages = list(python_extractor('filename', options))
    assert len(messages) == 1
    assert messages[0].comment == ''


@pytest.mark.usefixtures('fake_source')
def test_include_all_comments():
    global source
    options = mock.Mock()
    options.comment_tag = True
    source = u'''# source comment\n_(u'word')'''
    messages = list(python_extractor('filename', options))
    assert len(messages) == 1
    assert messages[0].comment == 'source comment'


@pytest.mark.usefixtures('fake_source')
def test_tagged_comment_on_previous_line():
    global source
    options = mock.Mock()
    options.comment_tag = 'I18N:'
    source = u'''# I18N: source comment\n_(u'word')'''
    messages = list(python_extractor('filename', options))
    assert len(messages) == 1
    assert messages[0].comment == 'source comment'


@pytest.mark.usefixtures('fake_source')
def test_tagged_multiline_comment():
    global source
    options = mock.Mock()
    options.comment_tag = 'I18N:'
    source = u'''# I18N: one\n# I18N: two\n_(u'word')'''
    messages = list(python_extractor('filename', options))
    assert len(messages) == 1
    assert messages[0].comment == 'one two'


@pytest.mark.usefixtures('fake_source')
def test_domain_filter():
    global source
    options = mock.Mock()
    options.domain = 'other'
    source = u'''dgettext('mydomain', 'word')'''
    messages = list(python_extractor('filename', options))
    assert len(messages) == 0
    options.domain = 'mydomain'
    messages = list(python_extractor('filename', options))
    assert len(messages) == 1


def test_dynamic_argument():
    global source
    options = mock.Mock()
    options.comment_tag = 'I18N:'
    source = u'''_('word', mapping={'foo': 2})'''
    messages = list(python_extractor('filename', options))
    assert len(messages) == 1
    assert messages[0].msgid == 'word'
