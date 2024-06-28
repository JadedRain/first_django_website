from typing import Any
from django.db.models import F
from django.db.models.query import QuerySet
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.utils import timezone

from .models import Question, Choice

class IndexView(generic.ListView):
    template_name = "polls/index.html"
    context_object_name = "latest_question_list"
    
    def get_queryset(self):
        """
        Return the last five published question (not including those set to be published in the future)
        """
        # valid_pages = []
        # for item in Question.objects.all():
        #     if item.choices_count() > 0:
        #         valid_pages.append(item)
        #     if len(valid_pages) > 5:
        #         return valid_pages
        return Question.objects.filter(choice__gte=1).order_by("-pub_date")[:5]
        
        # return Question.objects.filter(pub_date__lte=timezone.now()).order_by("-pub_date")[:5] 
    
class DetailView(generic.DetailView):
    model = Question
    template_name = "polls/detail.html"

    def get_queryset(self):
        """
        Excludes questions that aren't published yet
        """
        return Question.objects.filter(pub_date__lte=timezone.now())

class ResultsView(generic.DeleteView):
    model = Question
    template_name = "polls/results.html"

    def get_queryset(self):
        return Question.objects.filter(pub_date__lte=timezone.now())

def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        return render(
            request,
            "polls/detail.html",
            {
                "question": question,
                "error_message": "You didn't select a choice.",
            },
        )
    else:
        selected_choice.votes = F("votes") + 1
        selected_choice.save()
        return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))
