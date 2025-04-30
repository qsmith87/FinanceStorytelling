from django import forms

class TickerFileUploadForm(forms.Form):
    ticker = forms.CharField(required=False)
    pdf_file = forms.FileField(required=False)
    html_file = forms.FileField(required=False)

    def clean(self):
        cleaned_data = super().clean()
        ticker = cleaned_data.get('ticker')
        pdf_file = cleaned_data.get('pdf_file')
        html_file = cleaned_data.get('html_file')

        if not ticker and not pdf_file and not html_file:
            raise forms.ValidationError('Please provide a ticker, PDF file, or HTML file.')
        return cleaned_data
