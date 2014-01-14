from flask_wtf import Form
from wtforms import TextField, TextAreaField, HiddenField, SubmitField, PasswordField, BooleanField,\
    SelectMultipleField, RadioField, Label, widgets, SelectField
from pagedown import PageDownField
from wtforms.validators import Required, Length, Regexp


class MultiCheckboxField(SelectMultipleField):
    """
    A multiple-select, except displays a list of checkboxes.

    Iterating the field will produce subfields, allowing custom rendering of
    the enclosed checkbox fields.
    """
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class ImageLabel(Label):
    def __init__(self, field_id, text):
        super(ImageLabel, self).__init__(field_id, text)

    def __call__(self, text=None, **kwargs):
        if 'for_' in kwargs:
            kwargs['for'] = kwargs.pop('for_')
        else:
            kwargs.setdefault('for', self.field_id)

        attributes = widgets.html_params(**kwargs)
        return widgets.HTMLString('<label %s><img style="width: 100%%" src=%s /></label>'
                                  % (attributes, text or self.text))


class ImageField(HiddenField):
    def __init__(self, label=None, validators=None, filters=tuple(),
                 description='', id=None, default=None, widget=None,
                 _form=None, _name=None, _prefix='', _translations=None):
        super(ImageField, self).__init__(label, validators, filters, description, id, default, widget, _form, _name,
                                         _prefix, _translations)
        self.label = ImageLabel(self.id, label if label is not None else self.gettext(_name.replace('_', ' ').title()))

    def set_data(self, data, label):
        self.data = data
        self.label.text = label


class CommentRespondForm(Form):
    body = TextAreaField('body', validators=[Required()])
    email = TextField('Email', validators=[Length(min=6, max=35)])
    author = TextField('Name', validators=[Length(min=4, max=25)])
    comment_post_id = HiddenField('Post id', validators=[Required()])
    comment_parent_id = HiddenField('Parent id', default=0)


class EditArticleForm(Form):
    title = TextField('Title', validators=[Required(), Length(max=255)])
    pagedown = PageDownField('Enter your markdown')
    description = TextAreaField('Description', validators=[Length(max=350)])
    categories = MultiCheckboxField('Categories', coerce=int)
    image = ImageField('Image File')
    submit = SubmitField('Submit')


class LoginForm(Form):
    username = TextField('Username', validators=[Required()])
    password = PasswordField('Password', validators=[Required()])
    remember_me = BooleanField('remember_me', default=False)


class MediaForm(Form):
    files = RadioField('Files')