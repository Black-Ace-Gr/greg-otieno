from django.shortcuts import get_object_or_404, render

from .models import Achievement, Education, Profile, Project


def home(request):
    projects = list(Project.objects.filter(published=True))
    sections = []
    for value, label in Project.Category.choices:
        items = [p for p in projects if p.category == value]
        if items:
            sections.append({"slug": value, "label": label, "projects": items})
    return render(request, "portfolio/home.html", {
        "profile": Profile.objects.first(),
        "education": Education.objects.all(),
        "achievements": Achievement.objects.all(),
        "sections": sections,
    })


def project_detail(request, slug):
    project = get_object_or_404(Project, slug=slug, published=True)
    return render(request, "portfolio/project_detail.html", {
        "profile": Profile.objects.first(),
        "project": project,
    })
