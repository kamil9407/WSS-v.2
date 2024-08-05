from django.db import models, transaction, IntegrityError
import uuid
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.dispatch import receiver
from django.db.models.signals import post_save


def validate_pal_code(value):
    if not value.startswith('P'):
        raise ValidationError('Pallet code is not valid. Wrong validation letter.')

    if len(value) != 12:
        raise ValidationError('Pallet code length is not matching.')

def validate_ean(value):
    if len(value) !=13:
        raise ValidationError('EAN code is too short.')



def generate_pid():
    last_pallet = WarehousePallet.objects.all().order_by('id').last()
    if not last_pallet:
        new_pid = 'PL0000000'
    else:
        last_pid = last_pallet.pid[2:]
        new_pid_int = int(last_pid) + 1
        new_pid = f'PL{new_pid_int:07d}'
    return new_pid

def generate_sku():
    return str(uuid.uuid4()).split('-')[0]
# Model dostawcy
class Supplier(models.Model):
    
    name = models.CharField(max_length=255)
    address = models.TextField()

    def __str__(self):
        return self.name

# Model kategorii
class Category(models.Model):
    
    name = models.CharField(max_length=255)
    
    def __str__(self):
        return self.name

# Model towaru
class Cargo(models.Model):
    
    name = models.CharField(max_length=255)
    description = models.TextField(default = 'Add desc here')
    ean = models.CharField(max_length=13, validators = [validate_ean])
    pal_code = models.CharField(
        max_length = 12, null = True,
        validators = [validate_pal_code],
        help_text = "Pallet code must starts with 'P' and be 12 characters long."
        )
    quantity = models.DecimalField(max_digits=6, decimal_places=0, default = 0)
    sku = models.CharField(max_length=8, primary_key = True, unique=True, editable=False, default = generate_sku)  # Generowany automatycznie przez system
    buy_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_buy_price = models.DecimalField(max_digits=10, decimal_places=2, default = 0)
    sell_price = models.DecimalField(max_digits=10, decimal_places=2, default = None)
    total_sell_price = models.DecimalField(max_digits=10, decimal_places=2, default = 0)
    image = models.ImageField(upload_to='images/',null=True)
    unit_weight = models.DecimalField(max_digits=6, decimal_places=2, default = None)
    total_weight = models.DecimalField(max_digits=6, decimal_places=2, default = None)
    date = models.DateField(default=timezone.now)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='supplier')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='category')

    
    def save(self, *args, **kwargs):
        if not self.sku:
            self.sku = str(uuid.uuid4())[:8]  # Generowanie SKU przy pierwszym zapisie
        self.total_buy_price = self.buy_price * self.quantity
        self.total_sell_price = self.sell_price * self.quantity
        self.total_weight = self.unit_weight * self.quantity
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name

class WarehousePallet (models.Model):
    pid = models.CharField(max_length=10, unique=True, editable=False, null = False, default = generate_pid) 
    cargo = models.ForeignKey(Cargo, on_delete=models.CASCADE, related_name='cargo')
    quantity = models.DecimalField(max_digits = 10, decimal_places = 2)
    u_weight = models.DecimalField(max_digits = 10, decimal_places = 2, default = 0)
    total_weight = models.DecimalField(max_digits=6, decimal_places=2, default = 0)
    is_assigned = models.BooleanField(default = False)

    def save(self, *args, **kwargs):
        # The problem was during assignation the stock quantity was changed. Solution is to update stock when pallet is freshly created.
        if not self.pk:  # only adjust inventory when the object is first created
            if self.quantity > self.cargo.quantity:
                raise ValidationError(f"Not enough {self.cargo.name} in stock.")
            self.cargo.quantity -= self.quantity
            self.cargo.save(update_fields=['quantity'])
        
        self.total_weight = self.cargo.unit_weight * self.quantity
        if self.total_weight > 50:
            raise ValidationError("Pallet cannot be heavier than 50kg.")
        
        super().save(*args, **kwargs)

    def assign(self):
        self.is_assigned = True
        self.save(update_fields=['is_assigned'])

    # def save(self, *args, **kwargs):
    #     if self.quantity > self.cargo.quantity:
    #         raise ValidationError (f"Not enough {self.cargo.name} in the stock.")
    #     self.cargo.quantity -= self.quantity
    #     self.cargo.save(update_fields = ['quantity'])
    #     self.total_weight = self.u_weight * self.quantity
    #     if self.total_weight >50:
    #         raise ValidationError(" Cargo cannot be heavier than 50kg.")
    #     super().save(*args, **kwargs)
    
    def __str__(self):
        return self.pid


class AssignationNumber(models.Model):
    assignation_number = models.CharField(max_length=10, unique = True, editable = False)

    def generate_assign_number(self):
        last_instance = AssignationNumber.objects.order_by('-id').first()
        if last_instance:
            last_number = int(last_instance.assignation_number[2:])
        else:
            last_number = 0
        
        new_number = last_number + 1
        return f"AN{new_number:07d}"
            

    def save(self, *args, **kwargs):
        if not self.pk:
            self.assignation_number = self.generate_assign_number()
            super().save(*args, **kwargs)
    
    def __str__(self):
        return self.assignation_number


    
class AssignedPallet(models.Model):
    aid = models.ForeignKey(AssignationNumber, on_delete = models.CASCADE) 
    pallet = models.ForeignKey(WarehousePallet, on_delete = models.CASCADE)
    is_assigned = models.BooleanField(default = False)
    
    def __str__(self):
        return self.aid

class RackPlace(models.Model):
    
    rid = models.CharField(max_length = 4, unique = True, default = 'Add')
    is_occupied = models.BooleanField(default = False)

    def __str__(self):
        return self.rid

#Funkcja przyjmowania towaru na magazyn. Zawiera: Nazwę, kod, opis, cenę, ilość i docelowy magazyn


    # pamiętaj o zaimportowaniu modeli
    #Stwórz modele odpowiadające elementom modelu AddWare
#Funkcja generowania raportu przyjęcia towaru. Zawiera dane z funkcji przyjęcia towaru na magazyn oraz datę i dodatkowe informacje dotyczące przyjęcia towaru.
#Postępuj wg informacji na stronie https://django-import-export.readthedocs.io/en/latest/getting_started.html
#Stworzono model pod dodawanie towaru z importu, następnie trzeba będzie zrobić formularz w bazie danych i na stronie


