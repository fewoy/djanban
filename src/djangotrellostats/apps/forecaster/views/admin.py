# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from decimal import Decimal

import numpy as np
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic.edit import DeleteView

from djangotrellostats.apps.base.decorators import member_required
from djangotrellostats.apps.forecaster.forms import UpdateForecasterForm, BuildForecasterForm, TestForecasterForm
from djangotrellostats.apps.forecaster.models import Forecaster


@member_required
def index(request):
    forecasters = Forecaster.objects.all().order_by("board", "model")
    replacements = {"forecasters": forecasters}
    return render(request, "forecaster/index.html", replacements)


# Delete a Forecaster
class ForecasterDelete(DeleteView):
    model = Forecaster
    success_url = reverse_lazy('forecaster:index')
    template_name = "forecaster/delete.html"
    pk_url_kwarg = "forecaster_id"


@member_required
def build_forecaster(request):
    if request.method == "POST":
        form = BuildForecasterForm(request.POST)
        if form.is_valid():
            form.save(commit=True)
            return HttpResponseRedirect(reverse("forecaster:index"))
    else:
        form = BuildForecasterForm()

    return render(request, "forecaster/build.html", {"form": form})


# Test a forecaster
@member_required
def test_forecaster(request, forecaster_id):
    forecaster = get_object_or_404(Forecaster, id=forecaster_id)
    if request.method == "POST":
        form = TestForecasterForm(request.POST)
        if form.is_valid():
            test_cards = forecaster.test_cards
            total_error = 0
            test_card_errors = []
            for test_card in test_cards:
                test_card_estimated_spent_time = float(forecaster.estimate_spent_time(test_card))
                test_card.estimated_spent_time = Decimal(test_card_estimated_spent_time).quantize(Decimal('1.000'))
                test_card.diff = test_card.spent_time - test_card.estimated_spent_time
                test_card.error = abs(test_card.diff)
                total_error += test_card.error
                test_card_errors.append(test_card.error)

            avg_error = np.mean(test_card_errors)
            std_dev_error = np.std(test_card_errors)
            replacements = {
                "form": form, "forecaster": forecaster, "test_cards": test_cards,
                "total_error": total_error, "avg_error": avg_error, "std_dev_error": std_dev_error
            }
            return render(request, "forecaster/test.html", replacements)
    else:
        form = TestForecasterForm()

    return render(request, "forecaster/test.html", {"form": form})


# Update a forecaster
@member_required
def update_forecaster(request, forecaster_id):
    forecaster = get_object_or_404(Forecaster, id=forecaster_id)
    if request.method == "POST":
        form = UpdateForecasterForm(request.POST)
        if form.is_valid():
            form.save(forecaster)
            return HttpResponseRedirect(reverse("forecaster:index"))
    else:
        form = UpdateForecasterForm()

    return render(request, "forecaster/update.html", {"form": form, "forecaster": forecaster})


# View a forecaster
@member_required
def view_forecaster(request, forecaster_id):
    forecaster = get_object_or_404(Forecaster, id=forecaster_id)
    return render(request, "forecaster/view.html", {"forecaster": forecaster})
