from django.db import models
from django.utils.text import slugify

from .storage import image_storage, raw_storage


class Profile(models.Model):
    name = models.CharField(max_length=120)
    headline = models.CharField(max_length=200, help_text="One line, e.g. Mechatronics engineering student and full stack developer")
    about = models.TextField(blank=True)
    photo = models.ImageField(upload_to="profile/", storage=image_storage, blank=True)
    location = models.CharField(max_length=120, blank=True)
    email = models.EmailField(blank=True)
    github = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    cv_file = models.FileField(upload_to="cv/", storage=raw_storage, blank=True, verbose_name="CV (PDF)")

    def __str__(self):
        return self.name


class Education(models.Model):
    institution = models.CharField(max_length=160)
    program = models.CharField(max_length=160)
    start_year = models.PositiveSmallIntegerField()
    end_year = models.PositiveSmallIntegerField(null=True, blank=True, help_text="Leave empty if ongoing")
    details = models.TextField(blank=True)
    order = models.PositiveSmallIntegerField(default=0, help_text="Lower numbers show first")

    class Meta:
        ordering = ["order", "-start_year"]
        verbose_name_plural = "education"

    def __str__(self):
        return f"{self.program}, {self.institution}"


class Achievement(models.Model):
    title = models.CharField(max_length=160)
    date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "-date"]

    def __str__(self):
        return self.title


class Project(models.Model):
    class Category(models.TextChoices):
        WEB = "web", "Web projects"
        MOBILE = "mobile", "Mobile app projects"
        GAME = "game", "Mobile games"
        AI = "ai", "AI-integrated projects"
        CAD = "autocad", "AutoCAD projects"
        MECH = "mechatronics", "Mechatronic projects"

    title = models.CharField(max_length=160)
    slug = models.SlugField(max_length=180, unique=True, blank=True)
    category = models.CharField(max_length=20, choices=Category.choices)
    summary = models.CharField(max_length=240, help_text="Shown on the project card")
    description = models.TextField(blank=True, help_text="Full details. Blank lines start a new paragraph.")
    tech = models.CharField(max_length=240, blank=True, help_text="Comma-separated, e.g. Django, Kotlin, Arduino")
    date = models.DateField(null=True, blank=True)
    live_url = models.URLField(blank=True)
    repo_url = models.URLField(blank=True)
    cover = models.ImageField(upload_to="projects/covers/", storage=image_storage, blank=True)
    published = models.BooleanField(default=True)
    order = models.PositiveSmallIntegerField(default=0, help_text="Lower numbers show first")

    class Meta:
        ordering = ["order", "-date", "-id"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title) or "project"
            slug, n = base, 2
            while Project.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug, n = f"{base}-{n}", n + 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def tech_list(self):
        return [t.strip() for t in self.tech.split(",") if t.strip()]


class ProjectImage(models.Model):
    project = models.ForeignKey(Project, related_name="images", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="projects/gallery/", storage=image_storage)
    caption = models.CharField(max_length=200, blank=True)


class ProjectDocument(models.Model):
    project = models.ForeignKey(Project, related_name="documents", on_delete=models.CASCADE)
    title = models.CharField(max_length=160)
    file = models.FileField(upload_to="projects/documents/", storage=raw_storage)

    def __str__(self):
        return self.title