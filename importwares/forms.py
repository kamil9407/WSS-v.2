from .models import Cargo, WarehousePallet, AssignedPallet, RackPlace
from django import forms
from django.forms import ModelForm
from django.forms.models import (
    inlineformset_factory,
    modelform_factory,
    modelformset_factory
)

class CargoForm(forms.ModelForm):
    class Meta:
        model = Cargo
        fields = ['name', 'category','description', 'ean','pal_code','quantity', 'buy_price','sell_price','unit_weight', 'image', 'supplier', 'date']

class PalletForm(forms.ModelForm):
    class Meta:
        model = WarehousePallet
        fields = ['cargo','quantity']
    

class SearchForm(forms.Form):
    query = forms.CharField(label = 'Search', max_length = 255 )
        
class AssignationForm(forms.ModelForm):
    class Meta:
        model = AssignedPallet
        fields = ['pallet', 'is_assigned']

class RackPlaceForm(forms.ModelForm):
    class Meta:
        model = RackPlace
        fields = ['rid', 'is_occupied']

