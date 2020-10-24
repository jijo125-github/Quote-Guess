from django import forms

class AnswerValid(forms.Form):
    user_answer = forms.CharField(max_length=100)