from django import forms
from crispy_forms.helper import FormHelper

class SearchForm(forms.Form):
    searchTerm = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Search here. E.g. CMPU 102 QA'})
        )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_labels = False 
        '''
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('searchTerm', css_class='form-control bd-highlight col-9 mr-2')

            )
        )
    '''

class AddCourseForm(forms.Form):
    selectedCourse = forms.CharField(
                widget=forms.TextInput(attrs={'placeholder': 'Search here. E.g. CMPU 102 QA'})
        )

