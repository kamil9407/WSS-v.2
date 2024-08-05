from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from .models import Cargo, WarehousePallet, AssignedPallet, RackPlace
from .forms import CargoForm, PalletForm, SearchForm, AssignationForm
from django.http import HttpResponse
from django.template.loader import get_template, render_to_string
from xhtml2pdf import pisa
from django.core.exceptions import ValidationError
from django.shortcuts import render
from django.db.models import Q
from django import forms


def index(request):
    return render(request, 'importwares/index.html')



def generate_pdf(request):
    if request.method == 'POST':
        form = CargoForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.cleaned_data
            form.save()
            title = data['name']
            
            # Renderuj HTML za pomocą danych z formularza
            html = render_to_string('importwares/actions/report_template.html', {'data': data, 'title':title})
            
            # Generowanie PDF
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{{title}}.pdf"'
            pisa_status = pisa.CreatePDF(html, dest=response)
            
            if pisa_status.err:
                return HttpResponse('Błąd podczas generowania PDF: %s' % pisa_status.err, status=500)
            return response
    else:
        form = CargoForm()
    
    return render(request, 'importwares/actions/import_ware.html', {'form': form},)

def cargo_details(request, sku):
    cargo = get_object_or_404(Cargo, sku=sku)
    return render(request, 'importwares/database/cargo_details.html',{'cargo':cargo})

def create_whole_report(request):
    template_path = 'importwares/database/report_all.html'
    wares = Cargo.objects.all()
    context = {'wares': wares}
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="report.pdf"'
    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(
        html, dest=response
    )

    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

def ware_list_view(request):
    cargos = Cargo.objects.all()
    return render(request, 'importwares/database/ware_list.html', {'cargos': cargos})

  
def create_pallet(request):
    if request.method == 'POST':
        form = PalletForm(request.POST)
        if form.is_valid():
            try:
                pallet = form.save(commit=False)
                pallet.save()
                  
            except ValidationError as e:
                form.add_error(None, e.message)
    else:
        form = PalletForm()
    return render(request, 'importwares/actions/create_pallet.html', {'form': form})

def pallet_list(request):
    pallets = WarehousePallet.objects.all()
    return render(request, 'importwares/database/pallet_list.html', {'pallets': pallets})

def rack_places(request):
    racks = RackPlace.objects.all()
    return render(request, 'importwares/database/rack_place_list.html', {'racks':racks})  

def search(request): 
    form = SearchForm()
    cargos = []
    pallets = []

    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            cargos = Cargo.objects.filter(
                Q(name__icontains=query) |
                Q(ean__icontains=query) 
            )
    return render (request, "importwares/database/search.html",{'form':form, 'cargos':cargos})


def update_cargo(request, sku):
    cargo = get_object_or_404(Cargo, sku = sku)

    if request.method == 'POST':
        form = CargoForm(request.POST, instance = cargo)
        if form.is_valid():
            form.save()
            return redirect('ware_list')
    else:
        form = CargoForm(instance = cargo)

        
    return render (request, 'importwares/actions/update_cargo.html', {'form': form,'cargo':cargo})

def assign_pallet(request):
    if request.method == 'POST':
        pid = request.POST.get('pid')
        if pid:
            pallet = get_object_or_404(WarehousePallet,pid=pid)
            pallet.is_assigned = True
            pallet.save()
            return HttpResponse(f"Pallet {pid} has been assigned.")
        else: 
            return HttpResponse("Please provide a valid PID.")
    return render(request, 'importwares/actions/assign_pallet.html')

def assigned_pallets(request):
    accepted = WarehousePallet.objects.filter(is_assigned = True)
    return render(request, 'importwares/database/assigned_pallets.html', {'accepted':accepted})

def add_to_rack(request):
    if request.method == 'POST':
        rack_id = request.POST.get('rack_id')
        pid = request.POST.get('pid')

        try:
            # Pobierz obiekt RackPlace, który nie jest zajęty
            rack_place = get_object_or_404(RackPlace, rid=rack_id, is_occupied=False)
            # Pobierz paletę, która jest przypisana
            pallet = get_object_or_404(WarehousePallet, pid=pid, is_assigned=True)

            # Aktualizuj RackPlace, aby oznaczyć, że jest teraz zajęty
            rack_place.is_occupied = True
            rack_place.save()

            # Możliwość przypisania palety do miejsca
            pallet.assign()
            return HttpResponse(f"Pallet {pid} assigned to rack {rack_id}.")
        except RackPlace.DoesNotExist:
            return HttpResponse("Invalid rack ID or rack is already occupied.")
        except WarehousePallet.DoesNotExist:
            return HttpResponse("Invalid pallet ID or pallet is not assigned.")

    return render(request, 'importwares/actions/add_to_rack.html')
