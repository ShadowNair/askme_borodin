from django.shortcuts import render
from django.shortcuts import redirect
from django.urls import reverse
from app import models, forms
from app.utils.paginator import paginate_queryset
from django.contrib import auth
from django.contrib.auth.decorators import login_required

QUASTIONS = [
    {
        'title': f'Title {i}',
        'id': i,
        'text': f'This text for questions # {i}',
        'image_path': 'img/hova.jpeg'
    } for i in range(30)
]


# Create your views here.

def index(request):
    quastions = models.Quastion.objects.get_new_quastion()
    page_obj = paginate_queryset(quastions, request, 5)
    return render(request, template_name='Home.html', context={"quastions": page_obj})


@login_required(redirect_field_name='login', login_url='/login')
def hot(request):
    quastions = models.Quastion.objects.get_popular()
    page_obj = paginate_queryset(quastions, request, 5)
    return render(request, template_name='Hot.html', context={'quastions': page_obj})


@login_required(redirect_field_name='login', login_url='/login')
def single_quastion(request, quastion_id):
    item = models.Quastion.objects.get(id=quastion_id)
    answers = models.Answer.objects.get_answers(item.id)
    answers = paginate_queryset(answers, request, 5)
    if request.method == "POST":
        answer_form = forms.AnswerForm(request.POST)
        if answer_form.is_valid():
            answer = answer_form.save(author=models.Profile.objects.get(user__username=request.user.username), quastion=models.Quastion.objects.get(id=item.id))
            if answer:
                answers = models.Answer.objects.get_answers(item.id)
                answers = paginate_queryset(answers, request, 5)
                item.answers_count += 1
                return render(request, 'Quastion.html', {"item": item, "answers":answers, "form": answer_form})
    if request.method == 'GET':
        answer_form = forms.AnswerForm()
    return render(request, 'Quastion.html', {"item": item, "answers":answers, "form": answer_form})


@login_required(redirect_field_name='login', login_url='/login')
def tag(request, tag_name):
    quastions = models.Quastion.objects.get_by_tag(tag_name)
    page_obj = paginate_queryset(quastions, request, 5)
    return render(request, 'Tag.html', {"quastions": page_obj, "tag": tag_name})


@login_required(redirect_field_name='login', login_url='/login')
def ask(request):
    if request.method == 'GET':
        form = forms.AskForm()
    if request.method == 'POST':
        form = forms.AskForm(request.POST)
        if form.is_valid():
            try:
                if not hasattr(request.user, 'profile'):
                    profile = models.Profile.objects.create(user=request.user)
                else:
                    profile = request.user.profile
                    
                quastion = form.save(author=profile)
                return redirect('single_quastion', quastion_id=quastion.id)
            except Exception as e:
                form.add_error(None, f"Error: {str(e)}")
    else:
        form = forms.AskForm()
    
    return render(request, 'Ask.html', {'form': form})

def login(request):
    form = forms.LoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid() and (user := auth.authenticate(request, **form.cleaned_data)):
        auth.login(request, user)
        return redirect(reverse('index'))
    return render(request, 'LogIn.html', {'form': form, 'errors': 'Wrong username or password' if request.method == 'POST' and form.is_valid() else ''})


def logout(request):
    auth.logout(request)
    return redirect(reverse('login'))


def settings(request):
    if request.method == "POST":
        user_from_db = models.User.objects.get(username=request.user.username)
        setting_form = forms.SettingsForm(request.POST, request.FILES, user_from_db)
        if setting_form.is_valid():
            user = setting_form.save(user=user_from_db)
            if user:
                auth.login(request, user)
                return redirect(reverse("settings"))
            else:
                setting_form.add_error("can not update user's data")
    if request.method == "GET":
        setting_form = forms.SettingsForm()
    return render(request, 'Settings.html', {'form': setting_form})


def register(request):
    if request.method == 'POST':
        form = forms.RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('login')
    else: 
        form = forms.RegisterForm()
    
    return render(request, 'Registration.html', {'form': form})