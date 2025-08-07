from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Note
from .forms import NoteForm
from question.models import Problem

@login_required
def list_notes(request):
    """展示当前用户的全部笔记"""
    notes = Note.objects.filter(user=request.user).select_related('problem')
    return render(request, 'notes/notes_list.html', {'notes': notes})

@login_required
def edit_note(request, problem_id):
    """写/修改笔记（每题一条）"""
    problem = get_object_or_404(Problem, id=problem_id)
    note, _ = Note.objects.get_or_create(user=request.user, problem=problem)
    if request.method == 'POST':
        form = NoteForm(request.POST, instance=note)
        if form.is_valid():
            form.save()
            return redirect('notes:list_notes')
    else:
        form = NoteForm(instance=note)
    return render(request, 'notes/edit_note.html', {
        'form': form,
        'problem': problem
    })

@login_required
def delete_note(request, problem_id):
    """删除笔记"""
    note = get_object_or_404(Note, user=request.user, problem_id=problem_id)
    if request.method == 'POST':
        note.delete()
        return redirect('notes:list_notes')
    return render(request, 'notes/confirm_delete.html', {'note': note})
