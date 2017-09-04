from django.utils import translation
from wagtailtinymce.rich_text import TinyMCERichTextArea
from django.conf import settings

class MyTinyMCE(TinyMCERichTextArea):
    def __init__(self, *args, **kwargs):
        translation.trans_real.activate(settings.LANGUAGE_CODE)
        super(MyTinyMCE, self).__init__(*args, **kwargs)