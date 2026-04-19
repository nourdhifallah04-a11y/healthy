import logging

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from myapp.forms import ProfilNutritionnelForm
from myapp.models import ProfilNutritionnel
    
logger = logging.getLogger(__name__)
# Liste des profils (optionnel)
@login_required
def profil_list(request):
    logger.info(f"[profil_list] Appel par user={request.user.id} ({request.user.email})")

    profils = ProfilNutritionnel.objects.filter(client__utilisateur=request.user)

    logger.debug(f"[profil_list] Profils trouvés : {profils.count()}")

    return render(request, 'nutrition/profil_list.html', {'profils': profils})


# Ajouter un profil
@login_required
def profil_create(request):
    if request.method == 'POST':
        form = ProfilNutritionnelForm(request.POST)
        if form.is_valid():
            profil = form.save(commit=False)
            profil.user = request.user
            profil.save()
            return redirect('profil_list')
    else:
        form = ProfilNutritionnelForm()
    return render(request, 'nutrition/profil_form.html', {'form': form})

# Modifier un profil
@login_required
def profil_update(request, pk):
    profil = get_object_or_404(ProfilNutritionnel, pk=pk, user=request.user)
    if request.method == 'POST':
        form = ProfilNutritionnelForm(request.POST, instance=profil)
        if form.is_valid():
            form.save()
            return redirect('profil_list')
    else:
        form = ProfilNutritionnelForm(instance=profil)
    return render(request, 'nutrition/profil_form.html', {'form': form})

# Supprimer un profil
@login_required
def profil_delete(request, pk):
    profil = get_object_or_404(ProfilNutritionnel, pk=pk, user=request.user)
    if request.method == 'POST':
        profil.delete()
        return redirect('profil_list')
    return render(request, 'nutrition/profil_confirm_delete.html', {'profil': profil})
