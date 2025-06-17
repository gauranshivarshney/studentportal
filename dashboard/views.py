from django.shortcuts import render, redirect
from django.contrib import messages
from . forms import *
from .models import *
from django.views import generic
import requests
import wikipedia
from wikipedia.exceptions import DisambiguationError, PageError
from django.contrib.auth.decorators import login_required

# Create your views here.
def home(request):
    return render(request, 'dashboard/home.html')

@login_required
def notes(request):
    if request.method == 'POST':
        form = NoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.user = request.user
            note.save()
            messages.success(request, "Notes added successfully!")
            return redirect('notes')
    else:
        form = NoteForm()
    note = Note.objects.filter(user=request.user)
    context = {'note': note, 'form': form}
    return render(request, 'dashboard/notes.html', context)

@login_required
def delete_note(request, pk=None):
    Note.objects.get(id=pk).delete()
    return redirect('notes')

class NotesDetailView(generic.DetailView):
    model = Note
    template_name = 'dashboard/notes_detail.html'

@login_required
def homework(request):
    if request.method == 'POST':
        form = HomeworkForm(request.POST)
        if form.is_valid():
            try:
                finished = request.POST['is_finished']
                if finished == 'on':
                    finished = True
                else:
                    finished = False
            except:
                finished = False
            homeworks = form.save(commit=False)
            homeworks.user = request.user
            homeworks.save()
            messages.success(request, "Homework added successfully!")
            return redirect('homework')
    else:
        form = HomeworkForm()
    homework = Homework.objects.filter(user=request.user, is_finished = False)
    homework_done = not homework.exists()
    context = {'homework' : homework, 'homework_done' : homework_done, 'form' : form}
    return render(request, 'dashboard/homework.html', context)

@login_required
def update_homework(request, pk=None):
    homework = Homework.objects.get(id=pk)
    if homework.is_finished == True:
        homework.is_finished = False
    else:
        homework.is_finished = True
    homework.save()
    return redirect('homework')

@login_required
def delete_homework(request, pk=None):
    Homework.objects.get(id=pk).delete()
    return redirect('homework')

@login_required
def todo(request):
    if request.method == "POST":
        form = TodoForm(request.POST)
        if form.is_valid():
            try:
                finished = request.POST['is_finished']
                if finished == 'on':
                    finished = True
                else:
                    finished = False
            except:
                finished = False
            todos = form.save(commit=False)
            todos.user = request.user
            todos.save()
            messages.success(request, "Todo added successfully!")
            return redirect('todo')
    else:
        form = TodoForm()
    todo = Todo.objects.filter(user=request.user, is_finished = False)
    todo_done = not todo.exists()
    context = {'todo' : todo, 'form' : form, 'todo_done' : todo_done}
    return render(request, 'dashboard/todo.html', context)

@login_required
def update_todo(request, pk=None):
    todo = Todo.objects.get(id=pk)
    if todo.is_finished == True:
        todo.is_finished = False
    else:
        todo.is_finished = True
    todo.save()
    return redirect('todo')

@login_required
def delete_todo(request, pk=None):
    Todo.objects.get(id=pk).delete()
    return redirect('todo')

@login_required
def books(request):
    if request.method == "POST":
        form = DashboardForm(request.POST)
        text = request.POST['text']
        url = "https://www.googleapis.com/books/v1/volumes?q=" + text
        r = requests.get(url)
        answer = r.json()
        result_list = []
        for i in range(10):
            result_dict = {
                'title' : answer['items'][i]['volumeInfo']['title'],
                'subtitle' : answer['items'][i]['volumeInfo'].get('subtitle'),
                'description' : answer['items'][i]['volumeInfo'].get('description'),
                'count' : answer['items'][i]['volumeInfo'].get('pageCount'),
                'categories' : answer['items'][i]['volumeInfo'].get('categories'),
                'rating' : answer['items'][i]['volumeInfo'].get('averageRating'),
                'thumbnail' : answer['items'][i]['volumeInfo'].get('imageLinks', {}).get('thumbnail'),
                'preview' : answer['items'][i]['volumeInfo'].get('previewLink')
            }
            result_list.append(result_dict)
            context = {'form' : form, 'results' : result_list}
        return render(request, 'dashboard/books.html', context)
    else:
        form = DashboardForm()
    context = {'form' : form}
    return render(request, 'dashboard/books.html', context)

@login_required
def dictionary(request):
    if request.method == "POST":
        form = DashboardForm(request.POST)
        text = request.POST['text']
        url = "https://api.dictionaryapi.dev/api/v2/entries/en/" + text
        r = requests.get(url)
        answer = r.json()
        try:
            phonetics = answer[0]['phonetics'][0].get('text', '')
            audio = answer[0]['phonetics'][0].get('audio', '')
            definition = answer[0]['meanings'][0]['definitions'][0].get('definition', '')
            example = answer[0]['meanings'][0]['definitions'][0].get('example', 'No example found.')
            context = {'form': form, 'input': text, 'phonetics': phonetics, 'audio': audio, 'definition': definition, 'example': example}
        except:
            context = {'form': form, 'input': ''}
        return render(request, 'dashboard/dictionary.html', context)
    else:
        form = DashboardForm()
    context = {'form' : form}
    return render(request, 'dashboard/dictionary.html', context)

@login_required
def wiki(request):
    if request.method == "POST":
        text = request.POST['text']
        form = DashboardForm(request.POST)
        try:
            search = wikipedia.page(text)
            context = {'form' : form, 'title' : search.title, 'link' : search.url, 'details' : search.summary}
        except DisambiguationError as e:
            context = {
                'form': form,
                'options': e.options,
                'error': f"'{text}' may refer to multiple things. Please be more specific.",
            }
        except PageError:
            context = {
                'form': form,
                'error': f"No page found for '{text}'."
            }
        except Exception as e:
            context = {
                'form': form,
                'error': str(e)
            }
        return render(request, 'dashboard/wiki.html', context)
    else:
        form = DashboardForm()
    context = {'form' : form}
    return render(request, 'dashboard/wiki.html', context)

def register(request):
    if request.method == "POST":
        form = UserRegForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, "Account created!")
            return redirect('login')
    else:
        form = UserRegForm()
    context = {'form' : form}
    return render(request, 'dashboard/register.html', context)

@login_required
def profile(request):
    homeworks = Homework.objects.filter(is_finished=False, user=request.user)
    todos = Todo.objects.filter(is_finished=False, user=request.user)
    if len(homeworks) == 0:
        homework_done = True
    else:
        homework_done = False
    if len(todos) == 0:
        todo_done = True
    else:
        todo_done = False
    context = {'homeworks' : homeworks, 'todos' : todos, 'homework_done' : homework_done, 'todo_done' : todo_done}
    return render(request, 'dashboard/profile.html', context)