from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class GroupCreationForm(FlaskForm):
    groupName = StringField('Group Name', validators=[DataRequired()], render_kw={"placeholder": "Group Name"})
    submit = SubmitField('Create Group')
