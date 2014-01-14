from wtforms.widgets import HTMLString, TextArea
from wtforms.fields import TextAreaField

pagedown_pre_html = '''
<div class="flask-pagedown form-group">
'''

pagedown_post_html = '''
</div>
<script type="text/javascript">
f = function() {
    if (typeof flask_pagedown_converter === "undefined")
        flask_pagedown_converter = new Markdown.Converter().makeHtml
    var textarea = document.getElementById("flask-pagedown-%s");
    var preview = document.createElement('div');
    preview.className = 'flask-pagedown-preview col-xs-12 col-md-6';
    textarea.parentNode.insertBefore(preview, textarea.nextSibling);
    textarea.onkeyup = function() { preview.innerHTML = flask_pagedown_converter(textarea.value); }
    textarea.onkeyup.call(textarea);
}
if (window.addEventListener)
    window.addEventListener("load", f, false);
else if (window.attachEvent)
    window.attachEvent("onload", f);
else
    f();
</script>
'''


class PageDown(TextArea):
    def __call__(self, field, **kwargs):
        html = super(PageDown, self).__call__(field, id='flask-pagedown-' + field.name,
                                              class_='flask-pagedown-input col-xs-12 col-md-6', **kwargs)
        return HTMLString(pagedown_pre_html + html + pagedown_post_html % field.name)


class PageDownField(TextAreaField):
    widget = PageDown()